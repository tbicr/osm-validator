from aiohttp import web
from routes import setup_routes
import argparse
import sys
import aiohttp_jinja2
import pathlib


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('host_port', nargs='?', default='127.0.0.1:8080')
    return parser

app = web.Application()
pars = create_parser()
namespace = pars.parse_args(sys.argv[1:])
host = ''
port = ''
if namespace.host_port:
    host = namespace.host_port.split(':')[0]
    port = int(namespace.host_port.split(':')[1])
# setup views and routes
setup_routes(app)
# web.run_app(app, host='127.0.0.1', port=8080)
web.run_app(app, host=host, port=port)
