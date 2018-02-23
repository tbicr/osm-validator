from geoalchemy2.shape import to_shape
from shapely.geometry import Point
from sqlalchemy import select

from osm_validator.conftest import AsyncMock
from osm_validator.models import Feature, Issue, OSMPoint, State
from osm_validator.validators.base import BaseValidator
from osm_validator.validators.processor import (
    init_database, init_validators, process_changes
)


async def test_osm_data_initialization__ok(app, mocker, pbf_file):
    # prepare
    async with app.db.acquire() as conn:
        await conn.execute(State.__table__.delete())

    pbf_file.create("""<?xml version='1.0' encoding='UTF-8'?>
        <osm version="0.6" generator="osmconvert 0.8.5">
            <bounds minlat="53.9022" minlon="27.5618" maxlat="53.9023" maxlon="27.562"/>
            <node id="4450963913" lat="53.902237" lon="27.5619144"
                  version="6" timestamp="2017-04-13T12:43:17Z" changeset="47741570"
                  uid="481934" user="iWowik">
                <tag k="name" v="Пачатак дарог Беларусi"/>
            </node>
        </osm>
    """.encode())
    mocker.patch('osm_validator.settings.OSM_INIT_PBF', 'file://' + pbf_file.name)
    mocker.patch('osm_validator.settings.OSM_INIT_SEQUENCE_NUMBER', 718)

    # run
    await init_database()

    async with app.db.acquire() as conn:
        # check that sequence number applied
        sequence_number = await conn.scalar(
            select([
                State.__table__.c.value,
            ]).where(
                State.__table__.c.key == State.StateKey.sequence_number
            )
        )
        assert sequence_number == 718

        # check that osm data applied
        osm_point = await (await conn.execute(select([
            OSMPoint.__table__.c.osm_id,
            OSMPoint.__table__.c.tags,
            OSMPoint.__table__.c.way,
        ]))).fetchone()
        assert osm_point.osm_id == 4450963913
        assert osm_point.tags['name'] == 'Пачатак дарог Беларусi'
        assert to_shape(osm_point.way) == Point(27.5619144, 53.902237)


async def test_osm_data_updating__ok(app, mocker):
    # prepare
    async with app.db.acquire() as conn:
        await conn.execute(State.__table__.delete())
        await conn.execute(
            State.__table__.insert().values(
                key=State.StateKey.sequence_number,
                value=718,
            )
        )
        await conn.execute(OSMPoint.__table__.delete())

    get_sequence_number_mock = mocker.patch(
        'osm_validator.validators.processor._get_latest_sequence_number')
    get_sequence_number_mock.return_value = 720
    get_osc_mock = mocker.patch('osm_validator.validators.processor._fetch_osc')
    get_osc_mock.return_value = """<?xml version='1.0' encoding='UTF-8'?>
        <osmChange version="0.6" generator="osmium/1.5.1">
            <create>
                <node id="242979058" version="1" timestamp="2017-12-04T15:38:41Z"
                      uid="648920" user="::::" changeset="54333540"
                      lat="54.6570185" lon="29.141428">
                    <tag k="name" v="Новалукомль"/>
                </node>
            </create>
        </osmChange>
    """.encode()
    mocker.patch('osm_validator.validators.base._validators', [])

    # run
    await process_changes()

    async with app.db.acquire() as conn:
        # check that sequence number update
        sequence_number = await conn.scalar(
            select([
                State.__table__.c.value,
            ]).where(
                State.__table__.c.key == State.StateKey.sequence_number
            )
        )
        assert sequence_number == 720

        # check that osm data updated
        osm_point = await (await conn.execute(select([
            OSMPoint.__table__.c.osm_id,
            OSMPoint.__table__.c.tags,
            OSMPoint.__table__.c.way,
        ]))).fetchone()
        assert osm_point.osm_id == 242979058
        assert osm_point.tags['name'] == 'Новалукомль'
        assert to_shape(osm_point.way) == Point(29.141428, 54.6570185)

    # check mocks called correctly
    assert get_sequence_number_mock.call_count == 1
    assert get_osc_mock.call_count == 2


async def test_validator_initialization__ok(app, mocker):
    # prepare
    async with app.db.acquire() as conn:
        await conn.execute(Issue.__table__.delete())
        await conn.execute(Feature.__table__.delete())
        await conn.execute(Feature.__table__.insert().values(
            handle='test_validator_exists',
        ))

    class TestValidatorExists(BaseValidator):
        handle = 'test_validator_exists'

        async def init(self):
            raise Exception()

    class TestValidatorNew(BaseValidator):
        handle = 'test_validator_new'

        async def init(self):
            return [Issue(handle=self.handle)]

    mocker.patch('osm_validator.validators.base._validators', [
        TestValidatorExists,
        TestValidatorNew,
    ])

    # run
    await init_validators()

    async with app.db.acquire() as conn:
        # check that issues opened
        issue, = await (await conn.execute(Issue.__table__.select())).fetchall()

        assert issue.handle == 'test_validator_new'
        assert issue.date_created is not None
        assert issue.changeset_created_id is None
        assert issue.user_created_id is None


async def test_validator_processing__ok(app, mocker):
    # prepare
    async with app.db.acquire() as conn:
        await conn.execute(State.__table__.delete())
        await conn.execute(
            State.__table__.insert().values(
                key=State.StateKey.sequence_number,
                value=719,
            )
        )
        await conn.execute(Issue.__table__.delete())
        await conn.execute(Feature.__table__.delete())
        await conn.execute(Feature.__table__.insert().values(handle='test'))
        issues = await (await conn.execute(
            Issue.__table__.insert().returning(Issue.__table__.c.id).values([{
                'handle': 'test',
                'user_created_id': 1,
            }, {
                'handle': 'test',
                'user_created_id': 2,
            }])
        )).fetchall()
        exist_issue_1, exist_issue_2 = issues

    class TestValidator(BaseValidator):
        prepare_called = None
        check_called = None

        async def prepare(self, change):
            self.prepare_called = change

        async def check(self, change):
            self.check_called = change
            return [
                Issue(handle='test', changeset_created_id=123, user_created_id=456),
            ], [
                Issue(id=exist_issue_1.id, changeset_closed_id=123, user_closed_id=456),
            ]

    get_sequence_number_mock = mocker.patch(
        'osm_validator.validators.processor._get_latest_sequence_number')
    get_sequence_number_mock.return_value = 720
    get_osc_mock = mocker.patch('osm_validator.validators.processor._fetch_osc')
    get_osc_mock.return_value = b''
    mocker.patch('osm_validator.validators.processor.parse_osc')
    mocker.patch('osm_validator.validators.processor._apply_osc_to_database', AsyncMock())
    mocker.patch('osm_validator.validators.base._validators', [TestValidator])

    # run
    await process_changes()

    async with app.db.acquire() as conn:
        # check that issues opened and closed
        issues = await (await conn.execute(
            Issue.__table__.select().order_by(Issue.__table__.c.id)
        )).fetchall()
        issue_1, issue_2, issue_3 = issues

        assert issue_1.id == exist_issue_1.id
        assert issue_1.changeset_closed_id == 123
        assert issue_1.user_closed_id == 456
        assert issue_1.date_closed is not None

        assert issue_2.id == exist_issue_2.id
        assert issue_2.date_closed is None

        assert issue_3.handle == 'test'
        assert issue_3.changeset_created_id == 123
        assert issue_3.user_created_id == 456
        assert issue_3.date_created is not None
        assert issue_3.date_closed is None
