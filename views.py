import aiohttp_jinja2  # noqa
from aiohttp import web
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import User, postgresql
from oauth import OSMOauthClient

client = OSMOauthClient()


async def index(request):
    if client.oauth_token:
        user, _ = await client.user_info()
        engine = create_engine(postgresql)
        Session = sessionmaker(bind=engine)
        session = Session()
        query = session.query(User).filter(User.osm_user
                                           == user['osm_user']).all()
        if not query:
            new_user = User(osm_uid=user['osm_uid'], osm_user=user['osm_user'])
            session.add(new_user)
            session.commit()
        session.close()
        return web.Response(text='NAME - {}'.format(user['osm_user']))
    return web.Response(text="""
            <ul>
                <li><a href="/oauth/login">Login with OSM</a></li>
            </ul>
        """, content_type="text/html")


async def oauth_login(request):
    request_token, request_token_secret, _ = await client.get_request_token()
    return web.HTTPFound(client.get_authorize_url(request_token))


async def oauth_complete(request):
    oauth_token, oauth_token_secret, _ = \
        await client.get_access_token(request.GET['oauth_token'])
    # client = OSMOauthClient(oauth_token=oauth_token, oauth_token_secret=oauth_token_secret) # noqa
    user, _ = await client.user_info()
    return web.HTTPFound('/')
