import asyncio
import os
import sys

import pytest

dirname = os.path.dirname(__file__)
sys.path.append(os.path.abspath(os.path.join(dirname, '../..')))

from osm_validator.app import build_application  # isort:skip  # noqa


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
