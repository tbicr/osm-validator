from aioauth_client import OAuth1Client
from aiohttp import web
from lxml import etree


class OSMOauthClient(OAuth1Client):
    """
    Documentation: https://wiki.openstreetmap.org/wiki/OAuth
    Another implementation:
     https://github.com/python-social-auth/social-core/blob/master/social_core/backends/openstreetmap.py
    """

    name = 'openstreetmap'
    request_token_url = 'https://www.openstreetmap.org/oauth/request_token'
    access_token_url = 'https://www.openstreetmap.org/oauth/access_token'
    authorize_url = 'https://www.openstreetmap.org/oauth/authorize'
    user_info_url = 'https://api.openstreetmap.org/api/0.6/user/details'

    async def user_info(self, loop=None, **kwargs):
        """Load user information from provider."""
        if not self.user_info_url:
            raise NotImplementedError('The provider doesnt support user_info method.')

        response = await self.request('GET', self.user_info_url, loop=loop, **kwargs)
        if response.status / 100 > 2:
            raise web.HTTPBadRequest(
                reason='Failed to obtain User information. HTTP status code: %s' %
                       response.status)
        data = await response.read()
        user = dict(self.user_parse(data))
        return user, data

    @staticmethod
    def user_parse(data):
        root = etree.fromstring(data)
        user = root[0]
        yield 'osm_uid', int(user.attrib['id'])
        yield 'osm_user', user.attrib['display_name']
