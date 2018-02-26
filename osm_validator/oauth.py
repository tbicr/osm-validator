import asyncio
from urllib.parse import parse_qsl

import aiohttp
import async_timeout
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

    async def _request(self, method, url, loop=None, timeout=None, **kwargs):
        """Make a request through AIOHTTP."""
        try:
            async with async_timeout.timeout(timeout):
                async with aiohttp.ClientSession(loop=loop) as session:
                    async with session.request(method, url, **kwargs) as response:

                        if response.status / 100 > 2:
                            raise web.HTTPBadRequest(
                                reason='HTTP status code: %s' % response.status)

                        if 'json' in response.headers.get('CONTENT-TYPE'):
                            data = await response.json()
                        elif 'text/xml' in response.headers.get('CONTENT-TYPE'):
                            data = await response.read()
                        else:
                            data = await response.text()
                            data = dict(parse_qsl(data))

                        return data
        except asyncio.TimeoutError:
            raise web.HTTPBadRequest(reason='HTTP timeout')

    async def user_info(self, loop=None, **kwargs):
        """Load user information from provider."""
        if not self.user_info_url:
            raise NotImplementedError('The provider doesnt support user_info method.')

        data = await self.request('GET', self.user_info_url, loop=loop, **kwargs)
        user = dict(self.user_parse(data))
        return user, data

    @staticmethod
    def user_parse(data):
        root = etree.fromstring(data)
        user = root[0]
        yield 'osm_uid', int(user.attrib['id'])
        yield 'osm_user', user.attrib['display_name']
