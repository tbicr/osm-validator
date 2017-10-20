import asyncio


def test_loop(loop):
    fut = asyncio.Future(loop=loop)
    loop.call_soon(fut.set_result, 1)
    ret = loop.run_until_complete(fut)
    assert ret == 1
