import argparse
import asyncio
import sys

from aiohttp import web

import models
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
    if namespace.host_port:
        host = namespace.host_port.split(':')[0]
        port = int(namespace.host_port.split(':')[1])
    web.run_app(app, host=host, port=port)
