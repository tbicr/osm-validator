import asyncio
from sqlalchemy import Table, MetaData, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from aiopg.sa import create_engine
from settings import DATABASE
from sqlalchemy import create_engine


postgresql = 'postgresql://{}:{}@{}/{}'.format(DATABASE['user'], DATABASE['password'],
                                               DATABASE['host'], DATABASE['database'])
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


async def setup(app):
    engine = create_engine(postgresql)
    app['db_engine'] = engine
    app['db_declarative_base'] = Base

