import asyncio
from sqlalchemy import Table, MetaData, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from aiopg.sa import create_engine
from settings import DATABASE
from sqlalchemy import create_engine


postgresql = 'postgresql://{}:{}@{}/{}'.format(DATABASE['user'], DATABASE['password'],
                                                   DATABASE['host'], DATABASE['database'])
# declarate mapping
Base = declarative_base()


class UserOSM(Base):
    __tablename__ = 'UserOSM'

    osm_uid = Column(Integer, primary_key=True)
    osm_user = Column(String(50))

    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return "<UserOSM({},{})>".format(self.osm_uid, self.osm_user)


def run():
    # engine = create_engine('postgresql://jagrmi:1989@localhost/faust')
    engine = create_engine(postgresql)
    metadata = Base.metadata
    metadata.create_all(engine)
    return Base

async def setup(app):
    engine = create_engine(postgresql)
    metadata = Base.metadata
    metadata.create_all(engine)
    app['db_engine'] = engine
    app['db_declarative_base'] = Base
