import argparse
import asyncio

from aiohttp import web

from osm_validator.app import build_application

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-H', '--host', default='0.0.0.0')
    parser.add_argument('-P', '--port', type=int, default=8080)
    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(build_application())
    web.run_app(app, host=args.host, port=args.port)
