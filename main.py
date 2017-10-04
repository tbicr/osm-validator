from aiohttp import web
from routes import setup_routes
from db import close_pg, init_pg
import aiohttp_jinja2
import pathlib


app = web.Application()
# create connection to the database
app.on_startup.append(init_pg)
# shutdown db connection on exit
app.on_cleanup.append(close_pg)
# setup views and routes
setup_routes(app)
web.run_app(app, host='127.0.0.1', port=8080)
