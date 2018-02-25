"""init validator schema

Revision ID: acda10dff3fe
Revises:
Create Date: 2017-12-07 21:20:55.855630

"""
import geoalchemy2
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
from osm_validator.settings import PROJ

revision = 'acda10dff3fe'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Must be superuser to create this extension.
    # op.execute('CREATE EXTENSION hstore')
    # op.execute('CREATE EXTENSION postgis')
    op.create_table(
        'vld_user',
        sa.Column('osm_uid', sa.Integer(), nullable=False),
        sa.Column('osm_user', sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint('osm_uid')
    )
    op.create_table(
        'vld_state',
        sa.Column('key', sa.Enum('sequence_number', name='vld_statekey_enum'), nullable=False),
        sa.Column('value', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('key')
    )
    op.create_table(
        'vld_area',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('level', sa.SmallInteger(), nullable=False),
        sa.Column('name', sa.String(length=64), nullable=False),
        sa.Column('geom', geoalchemy2.types.Geometry(srid=PROJ), nullable=False),  # spatial index
        sa.ForeignKeyConstraint(['parent_id'], ['vld_area.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(
        'ix_vld_area_parent_id', 'vld_area', ['parent_id'],
        unique=False
    )
    op.create_table(
        'vld_feature',
        sa.Column('handle', sa.String(length=64), nullable=False),
        sa.Column('date_created', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('handle')
    )
    op.create_table(
        'vld_issue',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('handle', sa.String(length=64), nullable=False),
        sa.Column('changeset_created_id', sa.BigInteger(), nullable=True),
        sa.Column('changeset_closed_id', sa.BigInteger(), nullable=True),
        sa.Column('user_created_id', sa.BigInteger(), nullable=True),
        sa.Column('user_closed_id', sa.BigInteger(), nullable=True),
        sa.Column('date_created', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('date_closed', sa.DateTime(), nullable=True),
        sa.Column('affected_node_ids', postgresql.ARRAY(sa.BigInteger()), nullable=True),
        sa.Column('affected_way_ids', postgresql.ARRAY(sa.BigInteger()), nullable=True),
        sa.Column('affected_rel_ids', postgresql.ARRAY(sa.BigInteger()), nullable=True),
        sa.ForeignKeyConstraint(['handle'], ['vld_feature.handle'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(
        'ix_vld_issue_handle_affected_node_ids', 'vld_issue', ['handle', 'affected_node_ids'],
        unique=False, postgresql_where=sa.text('date_closed IS NOT NULL')
    )
    op.create_index(
        'ix_vld_issue_handle_affected_rel_ids', 'vld_issue', ['handle', 'affected_rel_ids'],
        unique=False, postgresql_where=sa.text('date_closed IS NOT NULL')
    )
    op.create_index(
        'ix_vld_issue_handle_affected_way_ids', 'vld_issue', ['handle', 'affected_way_ids'],
        unique=False, postgresql_where=sa.text('date_closed IS NOT NULL')
    )
    op.create_index(
        'ix_vld_issue_user_closed_id', 'vld_issue', ['user_closed_id'],
        unique=False
    )
    op.create_index(
        'ix_vld_issue_user_created_id', 'vld_issue', ['user_created_id'],
        unique=False
    )
    op.create_table(
        'vld_activity',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('name', sa.String(length=64), nullable=False),
        sa.Column('date_created', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['vld_user.osm_uid'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(
        'ix_vld_activity_user_id', 'vld_activity', ['user_id'],
        unique=False
    )
    op.create_table(
        'vld_activity_area',
        sa.Column('activity_id', sa.Integer(), nullable=False),
        sa.Column('area_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['activity_id'], ['vld_activity.id'], ),
        sa.ForeignKeyConstraint(['area_id'], ['vld_area.id'], ),
        sa.PrimaryKeyConstraint('activity_id', 'area_id')
    )
    op.create_table(
        'vld_activity_feature',
        sa.Column('activity_id', sa.Integer(), nullable=False),
        sa.Column('feature_handle', sa.String(length=64), nullable=False),
        sa.ForeignKeyConstraint(['activity_id'], ['vld_activity.id'], ),
        sa.ForeignKeyConstraint(['feature_handle'], ['vld_feature.handle'], ),
        sa.PrimaryKeyConstraint('activity_id', 'feature_handle')
    )


def downgrade():
    op.drop_table('vld_activity_feature')
    op.drop_table('vld_activity_area')
    op.drop_index('ix_vld_activity_user_id', table_name='vld_activity')
    op.drop_table('vld_activity')
    op.drop_index('ix_vld_issue_handle_affected_node_ids', table_name='vld_issue')
    op.drop_index('ix_vld_issue_handle_affected_way_ids', table_name='vld_issue')
    op.drop_index('ix_vld_issue_handle_affected_rel_ids', table_name='vld_issue')
    op.drop_index('ix_vld_issue_user_created_id', table_name='vld_issue')
    op.drop_index('ix_vld_issue_user_closed_id', table_name='vld_issue')
    op.drop_table('vld_issue')
    op.drop_table('vld_feature')
    op.drop_index('ix_vld_area_parent_id', table_name='vld_area')
    op.drop_table('vld_area')
    op.drop_table('vld_state')
    op.drop_table('vld_user')
