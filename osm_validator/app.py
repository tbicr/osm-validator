from aiohttp import web

from . import models, redis, routes, settings


async def close_redis(app):
    app.redis.close()
    await app.redis.wait_closed()


async def build_application():
    app = web.Application()
    app.config = settings

    await models.setup(app)
    app.on_cleanup.append(models.close)

    await redis.setup(app)
    app.on_shutdown.append(redis.close)

    await routes.setup(app)

    return app
