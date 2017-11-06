from aiopg.sa import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    osm_uid = Column(Integer, primary_key=True)
    osm_user = Column(String(50))

    def __init__(self, osm_uid, osm_user):
        self.osm_uid = osm_uid
        self.osm_user = osm_user

    def __repr__(self):
        return '<User: {} {}>'.format(self.osm_uid, self.osm_user)


async def setup(app):
    connection_url = 'postgresql://{}:{}@{}/{}'.format(
        app.config.DATABASE['user'],
        app.config.DATABASE['password'],
        app.config.DATABASE['host'],
        app.config.DATABASE['database'])
    engine = await create_engine(connection_url)
    app.db = engine
    app.db.Base = Base


async def close(app):
    app.db.close()
    await app.db.wait_closed()
    app.db = None
