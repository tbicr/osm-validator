import aiopg.sa
import sqlalchemy as sa


__all__ = ['user', 'area']

meta = sa.MetaData()


user = sa.Table(
    'user', meta,
    sa.Column('id', sa.Integer, nullable=False),
    sa.Column('user_name', sa.String(200), nullable=False),

    # Indexes #
    sa.PrimaryKeyConstraint('id', name='user_name_id_pkey'))

area = sa.Table(
    'area', meta,
    sa.Column('id', sa.Integer, nullable=False),
    sa.Column('user_id', sa.Integer, nullable=False),
    sa.Column('area_text', sa.String(200), nullable=False),
    sa.Column('user_activity_areas', sa.Integer, server_default="0", nullable=False),

    # Indexes #
    sa.PrimaryKeyConstraint('id', name='area_id_pkey'),
)


class RecordNotFound(Exception):
    """Requested record in database was not found"""


async def init_pg(app):
    conf = app['config']['postgres']
    engine = await aiopg.sa.create_engine(
        database=conf['database'],
        user=conf['user'],
        password=conf['password'],
        host=conf['host'],
        port=conf['port'],
        minsize=conf['minsize'],
        maxsize=conf['maxsize'],
        loop=app.loop)
    app['db'] = engine


async def close_pg(app):
    app['db'].close()
    await app['db'].wait_closed()