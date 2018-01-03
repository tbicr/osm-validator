import enum

from aiopg.sa import create_engine
from geoalchemy2 import Geometry
from sqlalchemy import (
    BigInteger, Column, DateTime, Enum, Float, ForeignKey, Index, SmallInteger,
    String, func
)
from sqlalchemy.dialects.postgresql import ARRAY, HSTORE, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class OSMNode(Base):
    """Raw OSM nodes data."""
    __tablename__ = 'osm_nodes'
    keep_existing = True

    id = Column(BigInteger, primary_key=True)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    tags = Column(ARRAY(String), nullable=True)

    def __repr__(self):
        return '<OSMNode: {}>'.format(self.id)


class OSMWay(Base):
    """Raw OSM ways data."""
    __tablename__ = 'osm_ways'
    keep_existing = True

    id = Column(BigInteger, primary_key=True)
    nodes = Column(ARRAY(BigInteger), nullable=False, index=True)
    tags = Column(ARRAY(String), nullable=True)

    def __repr__(self):
        return '<OSMWay: {}>'.format(self.id)


class OSMRel(Base):
    """Raw OSM relations data."""
    __tablename__ = 'osm_rels'
    keep_existing = True

    id = Column(BigInteger, primary_key=True)
    way_off = Column(SmallInteger, nullable=True)
    rel_off = Column(SmallInteger, nullable=True)
    parts = Column(ARRAY(BigInteger), nullable=True, index=True)
    members = Column(ARRAY(String), nullable=True)
    tags = Column(ARRAY(String), nullable=True)

    def __repr__(self):
        return '<OSMRel: {}>'.format(self.id)


class OSMPoint(Base):
    """Geometry built OSM nodes data."""
    __tablename__ = 'osm_point'
    keep_existing = True

    osm_id = Column(BigInteger, primary_key=True)
    tags = Column(HSTORE, nullable=True, index=True)
    way = Column(Geometry('POINT'), nullable=True, index=True)

    def __repr__(self):
        return '<OSMPoint: {}>'.format(self.osm_id)


class OSMLine(Base):
    """Geometry built OSM ways data."""
    __tablename__ = 'osm_line'
    keep_existing = True

    osm_id = Column(BigInteger, primary_key=True)
    tags = Column(HSTORE, nullable=True, index=True)
    way = Column(Geometry('LINE'), nullable=True, index=True)

    def __repr__(self):
        return '<OSMLine: {}>'.format(self.osm_id)


class OSMPolygon(Base):
    """Geometry built OSM ways and relations data."""
    __tablename__ = 'osm_polygon'
    keep_existing = True

    osm_id = Column(BigInteger, primary_key=True)
    tags = Column(HSTORE, nullable=True, index=True)
    way = Column(Geometry('POLYGON'), nullable=True, index=True)

    def __repr__(self):
        return '<OSMPolygon: {}>'.format(self.osm_id)


class User(Base):
    __tablename__ = 'vld_user'

    osm_uid = Column(BigInteger, primary_key=True)
    osm_user = Column(String(255), nullable=False)

    def __init__(self, osm_uid, osm_user):
        self.osm_uid = osm_uid
        self.osm_user = osm_user

    def __repr__(self):
        return '<User: {} {}>'.format(self.osm_uid, self.osm_user)


class State(Base):
    __tablename__ = 'vld_state'

    class StateKey(enum.Enum):
        sequence_number = 'sequence_number'

    key = Column(Enum(StateKey, name='vld_statekey_enum'), primary_key=True)
    value = Column(JSON(), nullable=True)

    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __repr__(self):
        return '<State: {} {}>'.format(self.key, self.value)


class Feature(Base):
    __tablename__ = 'vld_feature'

    handle = Column(String(64), primary_key=True)
    date_created = Column(DateTime, nullable=False, server_default=func.now())

    def __repr__(self):
        return '<Feature: {}>'.format(self.handle)


class Issue(Base):
    __tablename__ = 'vld_issue'

    id = Column(BigInteger, primary_key=True)
    handle = Column(String(64), ForeignKey('vld_feature.handle'), nullable=False)
    changeset_created = Column(BigInteger, nullable=True)
    changeset_closed = Column(BigInteger, nullable=True)
    user_created = Column(BigInteger, nullable=True, index=True)
    user_closed = Column(BigInteger, nullable=True, index=True)
    date_created = Column(DateTime, nullable=False, server_default=func.now())
    date_closed = Column(DateTime, nullable=True)
    affected_nodes = Column(ARRAY(BigInteger), nullable=True)
    affected_ways = Column(ARRAY(BigInteger), nullable=True)
    affected_rels = Column(ARRAY(BigInteger), nullable=True)

    __table_args__ = (
        Index('ix_vld_issue_handle_affected_nodes', handle, affected_nodes,
              postgresql_where=(date_closed.isnot(None))),
        Index('ix_vld_issue_handle_affected_ways', handle, affected_ways,
              postgresql_where=(date_closed.isnot(None))),
        Index('ix_vld_issue_handle_affected_rels', handle, affected_rels,
              postgresql_where=(date_closed.isnot(None))),
    )

    def __init__(self, id=None, handle=None, changeset_created=None, changeset_closed=None,
                 user_created=None, user_closed=None, date_created=None, date_closed=None,
                 affected_nodes=None, affected_ways=None, affected_rels=None):
        self.id = id
        self.handle = handle
        self.changeset_created = changeset_created
        self.changeset_closed = changeset_closed
        self.user_created = user_created
        self.user_closed = user_closed
        self.date_created = date_created
        self.date_closed = date_closed
        self.affected_nodes = affected_nodes
        self.affected_ways = affected_ways
        self.affected_rels = affected_rels

    def __repr__(self):
        return '<Issue: {} {}>'.format(self.handle, self.id)


async def setup(app):
    connection_url = 'postgresql://{}:{}@{}/{}'.format(
        app.config.DATABASE['user'],
        app.config.DATABASE['password'],
        app.config.DATABASE['host'],
        app.config.DATABASE['database'])
    engine = await create_engine(connection_url)
    engine.Base = Base
    app.db = engine


async def close(app):
    app.db.close()
    await app.db.wait_closed()
    app.db = None
