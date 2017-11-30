import base64

from aiohttp import web
from aiohttp_session import setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from cryptography.fernet import Fernet

from . import models, redis, routes, settings


async def close_redis(app):
    app.redis.close()
    await app.redis.wait_closed()


async def build_application():
    app = web.Application()

    fernet_key = Fernet.generate_key()
    secret_key = base64.urlsafe_b64decode(fernet_key)
    setup(app=app, storage=EncryptedCookieStorage(secret_key=secret_key))

    app.config = settings

    await models.setup(app)
    app.on_cleanup.append(models.close)

    await redis.setup(app)
    app.on_shutdown.append(redis.close)

    await routes.setup(app)

    return app
