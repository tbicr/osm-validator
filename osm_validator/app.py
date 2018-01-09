import base64

from aiohttp import web
from aiohttp_session import setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage

from . import models, redis, routes, settings


async def close_redis(app):
    app.redis.close()
    await app.redis.wait_closed()


async def build_application():
    app = web.Application()

    setup(app=app, storage=EncryptedCookieStorage(
        secret_key=base64.urlsafe_b64decode(settings.SECRET_KEY)))

    app.config = settings

    await models.setup(app)
    app.on_cleanup.append(models.close)

    await redis.setup(app)
    app.on_shutdown.append(redis.close)

    await routes.setup(app)

    return app
