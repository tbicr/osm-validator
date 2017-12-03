import json
import time

from cryptography.fernet import Fernet

from osm_validator.models import User


def make_cookie(client, fernet, data):
    session_data = {
        'session': data,
        'created': int(time.time())
    }

    cookie_data = json.dumps(session_data).encode('utf-8')
    data = fernet.encrypt(cookie_data).decode('utf-8')

    client.session.cookie_jar.update_cookies({'AIOHTTP_SESSION': data})


async def test_oauth_new_user__ok(app, client, mocker):
    async def get_request_token():
        return 'REQUEST_TOKEN', 'REQUEST_SECRET', None

    get_request_token_mock = mocker.patch('osm_validator.oauth.OSMOauthClient.get_request_token')
    get_request_token_mock.return_value = get_request_token()

    url = app.router['oauth:login'].url_for()
    response = await client.get(url, allow_redirects=False)
    assert response.status == 302
    assert response.headers['Location'] == ('https://www.openstreetmap.org/oauth/authorize?'
                                            'oauth_token=None')
    assert await app.redis.oauth.get('REQUEST_TOKEN') == 'REQUEST_SECRET'

    async def get_access_token():
        return 'REQUEST_TOKEN', 'REQUEST_SECRET', None

    get_access_token_mock = mocker.patch('osm_validator.oauth.OSMOauthClient.get_access_token')
    get_access_token_mock.return_value = get_access_token()

    async def user_info():
        return {'osm_uid': 1, 'osm_user': 'test'}, None

    user_info_mock = mocker.patch('osm_validator.oauth.OSMOauthClient.user_info')
    user_info_mock.return_value = user_info()

    url = app.router['oauth:complete'].url_for().with_query({'oauth_token': 'REQUEST_TOKEN'})
    response = await client.get(url)
    assert response.status == 200
    async with app.db.acquire() as conn:
        user = User(**await (await conn.execute(User.__table__.select())).fetchone())
    assert user.osm_uid == 1
    assert user.osm_user == 'test'

    async with app.db.acquire() as conn:
        await conn.execute(User.__table__.delete())


async def test_oauth_old_user__ok(app, client, mocker):
    async with app.db.acquire() as conn:
        await conn.execute(User.__table__.insert().values({
            'osm_uid': 1,
            'osm_user': 'test',
        }))

    async def get_request_token():
        return 'REQUEST_TOKEN', 'REQUEST_SECRET', None
    get_request_token_mock = mocker.patch('osm_validator.oauth.OSMOauthClient.get_request_token')
    get_request_token_mock.return_value = get_request_token()

    url = app.router['oauth:login'].url_for()
    response = await client.get(url, allow_redirects=False)
    assert response.status == 302
    assert response.headers['Location'] == ('https://www.openstreetmap.org/oauth/authorize?'
                                            'oauth_token=None')
    assert await app.redis.oauth.get('REQUEST_TOKEN') == 'REQUEST_SECRET'

    async def get_access_token():
        return 'REQUEST_TOKEN', 'REQUEST_SECRET', None
    get_access_token_mock = mocker.patch('osm_validator.oauth.OSMOauthClient.get_access_token')
    get_access_token_mock.return_value = get_access_token()

    async def user_info():
        return {'osm_uid': 1, 'osm_user': 'test 2'}, None
    user_info_mock = mocker.patch('osm_validator.oauth.OSMOauthClient.user_info')
    user_info_mock.return_value = user_info()

    url = app.router['oauth:complete'].url_for().with_query({'oauth_token': 'REQUEST_TOKEN'})
    response = await client.get(url)
    assert response.status == 200
    async with app.db.acquire() as conn:
        user = User(**await (await conn.execute(User.__table__.select())).fetchone())
    assert user.osm_uid == 1
    assert user.osm_user == 'test 2'

    async with app.db.acquire() as conn:
        await conn.execute(User.__table__.delete())


async def test_loggined_user__ok(app, client):
    async with app.db.acquire() as conn:
        await conn.execute(User.__table__.insert().values({
            'osm_uid': 1,
            'osm_user': 'user',
        }))
        user = User(**await (await conn.execute(User.__table__.select())).fetchone())

    url = app.router['index'].url_for()
    make_cookie(client, Fernet(app.config.SECRET_KEY), {'user_id': 1})
    response = await client.get(url)

    assert response.status == 200
    assert await response.text() == user.osm_user

    async with app.db.acquire() as conn:
        await conn.execute(User.__table__.delete())


async def test_unloaginneed_user__ok(app, client):
    url = app.router['index'].url_for()
    response = await client.get(url)

    assert response.status == 200
    assert await response.text() == 'Login required.'
