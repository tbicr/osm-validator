"""load initial osm pbf data

Revision ID: 72d184b925ac
Revises: acda10dff3fe
Create Date: 2017-12-24 15:09:52.221846

"""
import asyncio

from alembic import op

from osm_validator.validators.processor import init_database

# revision identifiers, used by Alembic.
revision = '72d184b925ac'
down_revision = 'acda10dff3fe'
branch_labels = None
depends_on = None


def upgrade():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init_database())


def downgrade():
    op.drop_table('osm_polygon')
    op.drop_table('osm_roads')
    op.drop_table('osm_line')
    op.drop_table('osm_point')
    op.drop_table('osm_rels')
    op.drop_table('osm_ways')
    op.drop_table('osm_nodes')
