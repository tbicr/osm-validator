import argparse
import asyncio
import sys

import aiohttp_jinja2
import jinja2
from aiohttp import web

import models
import settings
from models import close_pg, init_pg
from routes import setup_routes


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('host_port', nargs='?', default='127.0.0.1:8080')
    return parser


def build_application():
    loop = asyncio.get_event_loop()
    app = web.Application(loop=loop)
    loop.run_until_complete(models.setup(app))
    return app


if __name__ == '__main__':
    app = web.Application()
    setup_routes(app)
    pars = create_parser()
    namespace = pars.parse_args(sys.argv[1:])
    host = ''
    port = ''
    aiohttp_jinja2.setup(
        app=app,
        loader=jinja2.FileSystemLoader(settings.TEMPLATE_DIR),
        context_processors=[aiohttp_jinja2.request_processor], )
    app.on_startup.append(init_pg)
    app.on_cleanup.append(close_pg)
    if namespace.host_port:
        host = namespace.host_port.split(':')[0]
        port = int(namespace.host_port.split(':')[1])
    web.run_app(app, host=host, port=port)
