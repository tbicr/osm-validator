import logging
import os

BASE_DIR = os.path.dirname(__file__)
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')

DEBUG = False

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
logger.addHandler(console)

SECRET_KEY = os.environ['SECRET_KEY']

DATABASE = {
    'database': os.environ['PG_DATABASE'],
    'password': os.environ['PG_PASSWORD'],
    'user': os.environ['PG_USER'],
    'host': os.environ['PG_HOST'],
    'port': os.environ.get('PG_PORT', 5432),
}

REDIS = {
    'host': os.environ['REDIS_HOST'],
    'port': os.environ['REDIS_PORT'],
}

OAUTH_OPENSTREETMAP_KEY = os.environ['OAUTH_OPENSTREETMAP_KEY']
OAUTH_OPENSTREETMAP_SECRET = os.environ['OAUTH_OPENSTREETMAP_SECRET']
OAUTH_CACHE_EXPIRE = 3600

# for Belarus:
# OSM_INIT_PBF=http://download.geofabrik.de/europe/belarus-180101.osm.pbf
# OSM_INIT_SEQUENCE_NUMBER=1749
# OSM_CHANGE=http://download.geofabrik.de/europe/belarus-updates/
OSM_INIT_PBF = os.environ['OSM_INIT_PBF']
if OSM_INIT_PBF and '://' not in OSM_INIT_PBF:
    assert os.path.exists(OSM_INIT_PBF), '{} does not exist'.format(OSM_INIT_PBF)
    OSM_INIT_PBF = 'file://' + os.path.abspath(os.path.join(os.path.curdir, OSM_INIT_PBF))
OSM_INIT_SEQUENCE_NUMBER = int(os.environ['OSM_INIT_SEQUENCE_NUMBER'])
OSM_CHANGE = os.environ['OSM_CHANGE']
if OSM_CHANGE and '://' not in OSM_CHANGE:
    assert os.path.exists(OSM_CHANGE), '{} does not exist'.format(OSM_CHANGE)
    OSM_CHANGE = 'file://' + os.path.abspath(os.path.join(os.path.curdir, OSM_CHANGE))

OSM2PGSQL_CACHE = 4000
OSM2PGSQL_STYLE = './osm2pgslq.style'
assert os.path.exists(OSM2PGSQL_STYLE), '{} does not exist'.format(OSM2PGSQL_STYLE)

try:
    from .settings_local import *  # noqa
except ImportError:
    pass
