import enum

from aiopg.sa import create_engine
from geoalchemy2 import Geometry
from sqlalchemy import (
    BigInteger, CheckConstraint, Column, DateTime, Enum, Float, ForeignKey,
    Index, Integer, PrimaryKeyConstraint, SmallInteger, String, func
)
from sqlalchemy.dialects.postgresql import ARRAY, HSTORE, JSON
from sqlalchemy.ext.declarative import declarative_base

from osm_validator.settings import PROJ

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


class Area(Base):
    __tablename__ = 'vld_area'

    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('vld_area.id'), nullable=True, index=True)
    level = Column(SmallInteger, CheckConstraint('level > 0'), nullable=False)
    name = Column(String(64), nullable=False)
    geom = Column(Geometry('GEOMETRY', srid=PROJ, spatial_index=True), nullable=False)

    def __repr__(self):
        return '<Area: {} {}>'.format(self.level, self.name)


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
    changeset_created_id = Column(BigInteger, nullable=True)
    changeset_closed_id = Column(BigInteger, nullable=True)
    user_created_id = Column(BigInteger, nullable=True, index=True)
    user_closed_id = Column(BigInteger, nullable=True, index=True)
    date_created = Column(DateTime, nullable=False, server_default=func.now())
    date_closed = Column(DateTime, nullable=True)
    affected_node_ids = Column(ARRAY(BigInteger), nullable=True)
    affected_way_ids = Column(ARRAY(BigInteger), nullable=True)
    affected_rel_ids = Column(ARRAY(BigInteger), nullable=True)

    __table_args__ = (
        Index('ix_vld_issue_handle_affected_node_ids', handle, affected_node_ids,
              postgresql_where=(date_closed.isnot(None))),
        Index('ix_vld_issue_handle_affected_way_ids', handle, affected_way_ids,
              postgresql_where=(date_closed.isnot(None))),
        Index('ix_vld_issue_handle_affected_rel_ids', handle, affected_rel_ids,
              postgresql_where=(date_closed.isnot(None))),
    )

    def __init__(self, id=None, handle=None, changeset_created_id=None, changeset_closed_id=None,
                 user_created_id=None, user_closed_id=None, date_created=None, date_closed=None,
                 affected_node_ids=None, affected_way_ids=None, affected_rel_ids=None):
        self.id = id
        self.handle = handle
        self.changeset_created_id = changeset_created_id
        self.changeset_closed_id = changeset_closed_id
        self.user_created_id = user_created_id
        self.user_closed_id = user_closed_id
        self.date_created = date_created
        self.date_closed = date_closed
        self.affected_node_ids = affected_node_ids
        self.affected_way_ids = affected_way_ids
        self.affected_rel_ids = affected_rel_ids

    def __repr__(self):
        return '<Issue: {} {}>'.format(self.handle, self.id)


class Activity(Base):
    __tablename__ = 'vld_activity'

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('vld_user.osm_uid'), nullable=False, index=True)
    name = Column(String(64), nullable=False)
    date_created = Column(DateTime, nullable=False, server_default=func.now())

    def __repr__(self):
        return '<Activity: {} {}>'.format(self.user, self.name)


class ActivityArea(Base):
    __tablename__ = 'vld_activity_area'

    activity_id = Column(Integer, ForeignKey('vld_activity.id'))
    area_id = Column(Integer, ForeignKey('vld_area.id'))

    __table_args__ = (
        PrimaryKeyConstraint('activity_id', 'area_id'),
    )


class ActivityFeature(Base):
    __tablename__ = 'vld_activity_feature'

    activity_id = Column(Integer, ForeignKey('vld_activity.id'))
    feature_handle = Column(String(64), ForeignKey('vld_feature.handle'))

    __table_args__ = (
        PrimaryKeyConstraint('activity_id', 'feature_handle'),
    )


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
