import asyncio
import gzip
import logging
import os
import subprocess
from tempfile import NamedTemporaryFile
from urllib.parse import urljoin

import aiohttp
from sqlalchemy import func, select

from osm_validator.app import build_application
from osm_validator.models import Feature, Issue, State
from osm_validator.osm_change import parse_osc
from osm_validator.validators.base import Validator

logger = logging.getLogger()


def _get_latest_sequence_number(base_url):
    url = urljoin(base_url, 'state.txt')
    response = yield from asyncio.wait_for(aiohttp.request('get', url), 5)
    if response.status_code != 200:
        return None
    for line in response.text.splitlines():
        if line.startswith('sequenceNumber='):
            return int(line[len('sequenceNumber='):])
    return None


def _build_osc_url(base_url, sequence_number):
    seqno = str(sequence_number).zfill(9)
    return urljoin(base_url, '{}/{}/{}.osc.gz'.format(seqno[:3], seqno[3:6], seqno[6:]))


def _fetch_osc(url):
    response = yield from asyncio.wait_for(aiohttp.request('get', url), 30)
    response.raise_for_status()
    gzfile = gzip.GzipFile(fileobj=response.raw)
    return gzfile.read()


async def _init_database(app, conn, file_name):
    command = (
        'osm2pgsql --username {username} --host {host} --port {port} --database {database} '
        '--create --slim --cache {cache} --style {style} --prefix=osm '
        '--proj {proj} --hstore-all --hstore-add-index --multi-geometry '
        '--keep-coastlines --extra-attributes '
        '{file}'
    ).format(
        username=app.config.DATABASE['user'],
        host=app.config.DATABASE['host'],
        port=app.config.DATABASE['port'],
        database=app.config.DATABASE['database'],
        cache=app.config.OSM2PGSQL_CACHE,
        style=app.config.OSM2PGSQL_STYLE,
        proj=app.config.PROJ,
        file=file_name,
    )
    subprocess.run(command, shell=True, check=True)

    await conn.execute(
        State.__table__.insert().values(
            key=State.StateKey.sequence_number,
            value=app.config.OSM_INIT_SEQUENCE_NUMBER,
        )
    )


async def _apply_osc_to_database(app, conn, sequence_number, file_name):
    command = (
        'osm2pgsql --username {username} --host {host} --port {port} --database {database} '
        '--append --slim --cache {cache} --style {style} --prefix=osm '
        '--proj {proj} --hstore-all --hstore-add-index --multi-geometry '
        '--keep-coastlines --extra-attributes '
        '{file}'
    ).format(
        username=app.config.DATABASE['user'],
        host=app.config.DATABASE['host'],
        port=app.config.DATABASE['port'],
        database=app.config.DATABASE['database'],
        cache=app.config.OSM2PGSQL_CACHE,
        style=app.config.OSM2PGSQL_STYLE,
        proj=app.config.PROJ,
        file=file_name,
    )
    subprocess.run(command, shell=True, check=True)

    await conn.execute(
        State.__table__.update().where(
            State.__table__.c.key == State.StateKey.sequence_number
        ).values(
            value=sequence_number,
        )
    )


async def init_database():
    # run once with migration
    app = await build_application()
    try:
        session = aiohttp.ClientSession()
        logger.debug('Fetch init pdf file %s', app.config.OSM_INIT_PBF)
        response = session.get(url=app.config.OSM_INIT_PBF, stream=True)
        response.raise_for_status()
        with NamedTemporaryFile(suffix=os.path.splitext(app.config.OSM_INIT_PBF)[-1]) as handle:
            for block in response.iter_content(chunk_size=None):
                handle.write(block)
            handle.flush()
            logger.debug('Apply init pdf file %s', app.config.OSM_INIT_PBF)
            async with app.db.acquire() as conn:
                await _init_database(app, conn, handle.name)
    finally:
        await app.cleanup()


async def init_validators():
    # run every time on code restart (eg. new validator potential initialization)
    app = await build_application()
    try:
        async with app.db.acquire() as conn:
            validator = Validator(conn)
            ignore = {feature.handle for feature in await (await conn.execute(
                select([Feature.__table__.c.handle])
            )).fetchall()}
            logger.debug('Check and apply new validators init data')
            new = await validator.init(ignore=ignore)

            logger.debug('Save validators init %s new', len(new))
            if new:
                features = {issue.handle for issue in new}
                await conn.execute(Feature.__table__.insert().values([{
                    'handle': handle,
                } for handle in features]))
                await conn.execute(Issue.__table__.insert().values([{
                    'handle': issue.handle,
                    'date_created': func.now(),
                    'affected_node_ids': issue.affected_node_ids,
                    'affected_way_ids': issue.affected_way_ids,
                    'affected_rel_ids': issue.affected_rel_ids,
                } for issue in new]))
    finally:
        await app.cleanup()


async def process_changes():
    # run continuously
    app = await build_application()
    try:
        async with app.db.acquire() as conn:
            prev_sequence_number = await conn.scalar(
                select([
                    State.__table__.c.value,
                ]).where(
                    State.__table__.c.key == State.StateKey.sequence_number
                )
            )

            logger.debug('Fetch osm change state info %sstate.txt', app.config.OSM_CHANGE)
            new_sequence_number = _get_latest_sequence_number(app.config.OSM_CHANGE)
            if not new_sequence_number or prev_sequence_number >= new_sequence_number:
                return
            for sequence_number in range(prev_sequence_number + 1, new_sequence_number + 1):
                osc_url = _build_osc_url(app.config.OSM_CHANGE, sequence_number)

                logger.debug('Fetch osm change file %s', osc_url)
                osc_file = _fetch_osc(osc_url)
                osc_data = parse_osc(osc_file)
                validator = Validator(conn)

                logger.debug('Prepare changes by validators %s', osc_url)
                await validator.prepare(osc_data)

                logger.debug('Apply osm change file %s', osc_url)
                with NamedTemporaryFile(suffix='.osc') as handle:
                    handle.write(osc_file)
                    handle.flush()
                    await _apply_osc_to_database(app, conn, sequence_number, handle.name)

                logger.debug('Check changes by validators %s', osc_url)
                new, fixed = await validator.check(osc_data)

                logger.debug('Save validators changes %s new/%s fixed %s',
                             len(new), len(fixed), osc_url)
                if new:
                    await conn.execute(Issue.__table__.insert().values([{
                        'handle': issue.handle,
                        'changeset_created_id': issue.changeset_created_id,
                        'user_created_id': issue.user_created_id,
                        'date_created': func.now(),
                        'affected_node_ids': issue.affected_node_ids,
                        'affected_way_ids': issue.affected_way_ids,
                        'affected_rel_ids': issue.affected_rel_ids,
                    } for issue in new]))
                if fixed:
                    for issue in fixed:
                        await conn.execute(Issue.__table__.update().where(
                            Issue.__table__.c.id == issue.id
                        ).values(
                            changeset_closed_id=issue.changeset_closed_id,
                            user_closed_id=issue.user_closed_id,
                            date_closed=func.now(),
                        ))
    finally:
        await app.cleanup()
