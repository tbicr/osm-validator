import aiopg.sa
from aiopg.sa import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

from settings import DATABASE

postgresql = 'postgresql://{}:{}@{}/{}'.format(DATABASE['user'],
                                               DATABASE['password'],
                                               DATABASE['host'],
                                               DATABASE['database'])
# Declarate mapping
Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    osm_uid = Column(Integer, primary_key=True)
    osm_user = Column(String(50))

    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return "<user({},{})>".format(self.osm_uid, self.osm_user)


async def init_pg(app):
    engine = await aiopg.sa.create_engine(
        database=DATABASE['database'],
        user=DATABASE['user'],
        password=DATABASE['password'],
        host=DATABASE['host'],)
    app['db'] = engine


async def close_pg(app):
    app['db'].close()
    await app['db'].wait_closed()


async def setup(app):
    engine = create_engine(postgresql)
    app['db_engine'] = engine
    app['db_declarative_base'] = Base
