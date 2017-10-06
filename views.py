import aiohttp_jinja2

from aiohttp import web
from . import db


async def index(request):
    return web.Response(text='Hello world!')
