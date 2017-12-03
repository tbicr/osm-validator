from aiohttp import web
from aiohttp.web import middleware
from aiohttp_session import get_session, setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage

from . import models, redis, routes, settings


@middleware
async def user_middleware(request, handler):
    session = await get_session(request=request)
    user_id = session['user_id'] if 'user_id' in session else None
    request.user = user_id
    response = await handler(request)
    return response


async def close_redis(app):
    app.redis.close()
    await app.redis.wait_closed()


async def build_application():
    app = web.Application()

    setup(app=app, storage=EncryptedCookieStorage(secret_key=settings.SECRET_KEY))
    app.middlewares.append(user_middleware)

    app.config = settings

    await models.setup(app)
    app.on_cleanup.append(models.close)

    await redis.setup(app)
    app.on_shutdown.append(redis.close)

    await routes.setup(app)

    return app
