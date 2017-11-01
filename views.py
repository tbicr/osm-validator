from aiohttp import web

from oauth import OSMOauthClient


async def index(request):
    return web.Response(text='Hello world!')


async def oauth_login(request):
    request_token, _, _ = await OSMOauthClient().get_request_token()
    return web.HTTPFound(OSMOauthClient().get_authorize_url(request_token))


async def oauth_complete(request):
    oauth_token, oauth_token_secret, _ = await OSMOauthClient().get_access_token(request.GET['oauth_token'])
    client = OSMOauthClient(oauth_token=oauth_token, oauth_token_secret=oauth_token_secret)
    user, _ = await client.user_info()
    return web.HTTPFound('/')
