import base64
import json

from cryptography.fernet import Fernet

from osm_validator.models import User


def make_cookie(client, fernet, data):
    fernet_key = base64.urlsafe_b64encode(fernet)
    fernet_obj = Fernet(fernet_key)

    cookie_data = json.dumps(data).encode('utf-8')
    cookie_value = fernet_obj.encrypt(cookie_data).decode('utf-8')
    assert '=' in cookie_value
    client.session.cookie_jar.update_cookies({'AIOHTTP_SESSION': cookie_value})


def decrypt(fernet, cookie_value):
    fernet_key = base64.urlsafe_b64encode(fernet)
    fernet_obj = Fernet(fernet_key)

    assert type(cookie_value) == str
    return json.loads(
        fernet_obj.decrypt(cookie_value.encode('utf-8')).decode('utf-8')
    )


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


async def test_loggined_user__ok(app, client, mocker):
    url = app.router['test'].url_for()

    # Create record in database
    async with app.db.acquire() as conn:
        await conn.execute(User.__table__.insert().values({
            'osm_uid': 1,
            'osm_user': 'user',
        }))

    make_cookie(client, app.config.SECRET_KEY, {'user': 1})
    mocker(client, app.config.SECRET_KEY, {'user': 1})

    response = await client.get(url)

    # Get a record from database
    async with app.db.acquire() as conn:
        user = User(**await (await conn.execute(User.__table__.select())).fetchone())
    # Delete a record from database
    async with app.db.acquire() as conn:
        await conn.execute(User.__table__.delete())

    assert response.status == 200
    assert await response.text() == 'This is information about USER - {}'.format(user.osm_uid)


async def test_unloaginneed_user__ok(app, client):
    url = app.router['index'].url_for()
    response = await client.get(url)

    assert response.status == 200
    assert 'Users: 0' in await response.text()
