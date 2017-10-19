import asyncio

import pytest


@pytest.yield_fixture
def loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(None)

    yield loop

    if not loop.is_closed():
        loop.call_soon(loop.stop)
        loop.run_forever()
        loop.close()


@pytest.yield_fixture()
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
