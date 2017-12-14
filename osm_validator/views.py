from aiohttp import web
from aiohttp_session import get_session
from psycopg2._psycopg import IntegrityError

from . import models
from .oauth import OSMOauthClient


async def index(request):
    return web.FileResponse('./static/index.html')


async def oauth_login(request):
    oauth_client = OSMOauthClient(
        consumer_key=request.app.config.OAUTH_OPENSTREETMAP_KEY,
        consumer_secret=request.app.config.OAUTH_OPENSTREETMAP_SECRET)
    request_token, request_token_secret, _ = await oauth_client.get_request_token()
    await request.app.redis.oauth.set(
        request_token,
        request_token_secret,
        expire=request.app.config.OAUTH_CACHE_EXPIRE)
    return web.HTTPFound(oauth_client.get_authorize_url())


async def oauth_complete(request):
    session = await get_session(request=request)

    request_token = request.GET['oauth_token']
    request_token_secret = await request.app.redis.oauth.get(request_token)
    if request_token_secret is None:
        return web.HTTPFound(request.app.router['oauth:login'].url_for())

    oauth_client = OSMOauthClient(
        consumer_key=request.app.config.OAUTH_OPENSTREETMAP_KEY,
        consumer_secret=request.app.config.OAUTH_OPENSTREETMAP_SECRET,
        oauth_token=request_token,
        oauth_token_secret=request_token_secret)
    oauth_token, oauth_token_secret, _ = await oauth_client.get_access_token(
        request_token)
    oauth_client = OSMOauthClient(
        consumer_key=request.app.config.OAUTH_OPENSTREETMAP_KEY,
        consumer_secret=request.app.config.OAUTH_OPENSTREETMAP_SECRET,
        oauth_token=oauth_token,
        oauth_token_secret=oauth_token_secret)
    user, _ = await oauth_client.user_info()
    async with request.app.db.acquire() as conn:
        try:
            await conn.execute(models.User.__table__.insert().values(**user))
        except IntegrityError:
            await conn.execute(models.User.__table__.update().
                               where(models.User.__table__.c.osm_uid == user['osm_uid']).
                               values(**user))

    session['user_id'] = user['osm_uid']
    return web.HTTPFound(request.app.router['index'].url_for())


async def sign_out(request):
    session = await get_session(request=request)
    user_id = session['user_id'] if 'user_id' in session else None
    if user_id:
        del session['user_id']
    url = request.app.router['index'].url_for()
    return web.HTTPFound(url)


async def user_info(request):
    if request.user:
        user = {'osm_user': request.user.osm_user}
        return web.json_response(user, status=200)
    else:
        user = {'osm_user': 'undefined'}
        return web.json_response(user, status=400)
