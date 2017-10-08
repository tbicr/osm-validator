import sys
import os
import logging

BASE_DIR = os.path.dirname(__file__)
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')

HOST = '127.0.0.1'
PORT = '8080'

DEBUG = False

logger = logging.getLogger('app')
logger.setLevel(logging.DEBUG)
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
logger.addHandler(console)

DATABASE = {
    'database': '',
    'password': '',
    'user': '',
    'host': '',
}

try:
    from settings_local import *
except ImportError:
    pass
