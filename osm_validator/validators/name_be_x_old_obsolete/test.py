from datetime import datetime

from osm_validator.models import Feature, Issue, OSMPoint
from osm_validator.osm_change import parse_osc
from osm_validator.validators.name_be_x_old_obsolete import (
    NameBeXOldObsoleteValidator
)


CHANGE = parse_osc("""<?xml version='1.0' encoding='UTF-8'?>
<osmChange version="0.6" generator="osmium/1.5.1">
  <create>
    <node id="1" version="1" timestamp="2018-01-01T00:00:00Z"
          uid="123" user="osmvalidator" changeset="456"
          lat="54.6570185" lon="29.141428">
      <tag k="name:be-x-old" v="Менск"/>
      <tag k="place" v="town"/>
    </node>
  </create>
  <modify>
    <node id="2" version="1" timestamp="2018-01-01T00:00:00Z"
          uid="123" user="osmvalidator" changeset="456"
          lat="54.6570185" lon="29.141428">
      <tag k="name:be-x-old" v="Віцебск"/>
      <tag k="place" v="town"/>
    </node>
  </modify>
  <delete>
    <node id="3" version="1" timestamp="2018-01-01T00:00:00Z"
          uid="123" user="osmvalidator" changeset="456"
          lat="54.6570185" lon="29.141428">
      <tag k="name:be-x-old" v="Гародня"/>
      <tag k="place" v="town"/>
    </node>
  </delete>
  <modify>
    <node id="4" version="1" timestamp="2018-01-01T00:00:00Z"
          uid="123" user="osmvalidator" changeset="456"
          lat="54.6570185" lon="29.141428">
      <tag k="name:be-tarask" v="Магілёў"/>
      <tag k="place" v="town"/>
    </node>
  </modify>
  <modify>
    <node id="5" version="1" timestamp="2018-01-01T00:00:00Z"
          uid="123" user="osmvalidator" changeset="456"
          lat="54.6570185" lon="29.141428">
      <tag k="name:be-x-old" v="Гомель"/>
      <tag k="place" v="town"/>
    </node>
  </modify>
</osmChange>
""".encode())


async def test_name_be_x_old__init__ok(app):
    async with app.db.acquire() as conn:
        await conn.execute(Issue.__table__.delete())
        await conn.execute(OSMPoint.__table__.delete())
        await conn.execute(OSMPoint.__table__.insert().values([{
            'osm_id': 1,
            'tags': {'name:be-x-old': 'Менск'},
        }]))

        validator = NameBeXOldObsoleteValidator(conn)
        new = await validator.init()

        issue_1, = new
        assert issue_1.handle == 'name_be_x_old_obsolete'
        assert issue_1.changeset_created is None
        assert issue_1.user_created is None
        assert issue_1.date_created is None
        assert issue_1.affected_nodes == [1]


async def test_name_be_x_old__update_from_osc__ok(app):
    async with app.db.acquire() as conn:
        await conn.execute(Feature.__table__.delete())
        await conn.execute(Feature.__table__.insert().values(
            handle='name_be_x_old_obsolete',
        ))
        await conn.execute(Issue.__table__.delete())
        await conn.execute(Issue.__table__.insert().values([{
            'handle': 'name_be_x_old_obsolete',
            'affected_nodes': [3],
        }, {
            'handle': 'name_be_x_old_obsolete',
            'affected_nodes': [4],
        }, {
            'handle': 'name_be_x_old_obsolete',
            'affected_nodes': [5],
        }]))

        validator = NameBeXOldObsoleteValidator(conn)
        new, fixed = await validator.check(CHANGE)

        issue_1, issue_2 = sorted(new, key=lambda i: i.affected_nodes)
        issue_3, issue_4 = sorted(fixed, key=lambda i: i.affected_nodes)

        assert issue_1.handle == 'name_be_x_old_obsolete'
        assert issue_1.changeset_created == 456
        assert issue_1.user_created == 123
        assert issue_1.date_created == datetime(2018, 1, 1)
        assert issue_1.affected_nodes == [1]

        assert issue_2.handle == 'name_be_x_old_obsolete'
        assert issue_2.changeset_created == 456
        assert issue_2.user_created == 123
        assert issue_2.date_created == datetime(2018, 1, 1)
        assert issue_2.affected_nodes == [2]

        assert issue_3.handle == 'name_be_x_old_obsolete'
        assert issue_3.changeset_closed == 456
        assert issue_3.user_closed == 123
        assert issue_3.date_closed == datetime(2018, 1, 1)
        assert issue_3.affected_nodes == [3]

        assert issue_4.handle == 'name_be_x_old_obsolete'
        assert issue_4.changeset_closed == 456
        assert issue_4.user_closed == 123
        assert issue_4.date_closed == datetime(2018, 1, 1)
        assert issue_4.affected_nodes == [4]
