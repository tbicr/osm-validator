import os

from aioresponses import aioresponses

from osm_validator.oauth import OSMOauthClient


async def test_osm_oauth_client__ok():
    oauth_client = OSMOauthClient('', '')

    with aioresponses() as response_mocker:
        response_mocker.get(
            'https://www.openstreetmap.org/oauth/request_token', status=200,
            body=b'oauth_token=REQUEST_TOKEN&oauth_token_secret=REQUEST_SECRET')
        request_token, request_token_secret, _ = await oauth_client.get_request_token()
    assert request_token == 'REQUEST_TOKEN'
    assert request_token_secret == 'REQUEST_SECRET'

    url = oauth_client.get_authorize_url()
    assert url == 'https://www.openstreetmap.org/oauth/authorize?oauth_token=REQUEST_TOKEN'

    with aioresponses() as response_mocker:
        response_mocker.post(
            'https://www.openstreetmap.org/oauth/access_token', status=200,
            body=b'oauth_token=OAUTH_TOKEN&oauth_token_secret=OAUTH_SECRET')
        oauth_token, oauth_token_secret, _ = await oauth_client.get_access_token('REQUEST_TOKEN')
    assert oauth_token == 'OAUTH_TOKEN'
    assert oauth_token_secret == 'OAUTH_SECRET'

    osm_stub_user_details = os.path.join(os.path.dirname(__file__), 'osm_stub_user_details.xml')
    with aioresponses() as response_mocker:
        response_mocker.get(
            'https://api.openstreetmap.org/api/0.6/user/details', status=200,
            body=open(osm_stub_user_details, 'rb').read())
        user, _ = await oauth_client.user_info()
    assert user == {
        'osm_uid': 278800,
        'osm_user': 'Карыстальнік',
    }
