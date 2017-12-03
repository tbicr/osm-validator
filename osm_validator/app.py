import base64

from aiohttp import web
from aiohttp.web import middleware
from aiohttp_session import get_session, setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage

from . import models, redis, routes, settings


@middleware
async def user_middleware(request, handler):
    session = await get_session(request=request)
    request.user = None
    if 'user_id' in session:
        user_id = session['user_id']
        async with request.app.db.acquire() as conn:
            request.user = models.User(**await (await conn.execute(
                models.User.__table__.select().where(models.User.__table__.c.osm_uid == user_id))
            ).fetchone())
    response = await handler(request)
    return response


async def close_redis(app):
    app.redis.close()
    await app.redis.wait_closed()


async def build_application():
    app = web.Application()

    setup(app=app, storage=EncryptedCookieStorage(
        secret_key=base64.urlsafe_b64decode(settings.SECRET_KEY)))
    app.middlewares.append(user_middleware)

    app.config = settings

    await models.setup(app)
    app.on_cleanup.append(models.close)

    await redis.setup(app)
    app.on_shutdown.append(redis.close)

    await routes.setup(app)

    return app
