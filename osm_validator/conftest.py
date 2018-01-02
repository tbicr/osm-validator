import asyncio
import subprocess
from tempfile import NamedTemporaryFile
from unittest.mock import MagicMock

import pytest

from osm_validator.app import build_application


class AsyncMock(MagicMock):

    async def __call__(self, *args, **kwargs):
        return super(AsyncMock, self).__call__(*args, **kwargs)


@pytest.yield_fixture
def loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(None)

    yield loop

    if not loop.is_closed():
        loop.call_soon(loop.stop)
        loop.run_forever()
        loop.close()


@pytest.fixture
def app(loop):
    return loop.run_until_complete(build_application())


@pytest.fixture
async def client(loop, app, test_client):
    return await test_client(app)


class OSM2PBFWrapper(object):

    def __init__(self, pbf_handle, osm_handle):
        self.pbf_handle = pbf_handle
        self.osm_handle = osm_handle

    def __getattr__(self, item):
        return getattr(self.pbf_handle, item)

    def create(self, data):
        self.osm_handle.write(data)
        self.osm_handle.flush()
        command = 'osmconvert {} --out-pbf'.format(self.osm_handle.name)
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE)
        self.pbf_handle.write(result.stdout)
        self.pbf_handle.flush()


@pytest.yield_fixture
def pbf_file():
    with NamedTemporaryFile(suffix='.pbf') as pbf_handle:
        with NamedTemporaryFile(suffix='.osm') as osm_handle:
            yield OSM2PBFWrapper(pbf_handle, osm_handle)
