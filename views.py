import aiohttp_jinja2

from aiohttp import web
from . import db


@aiohttp_jinja2.template('index.html')
async def index(request):
    return web.Response(text='Hello world!')
