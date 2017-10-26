import aiohttp_jinja2
import psycopg2
from aiohttp import web  # noqa

from settings import DATABASE


@aiohttp_jinja2.template('index.html')
async def index(request):
    conn = psycopg2.connect(dbname=DATABASE['database'],
                            user=DATABASE['user'],
                            password=DATABASE['password'],
                            host=DATABASE['host'])
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM "user"')
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return {'users': users}
