"""init validator schema

Revision ID: acda10dff3fe
Revises:
Create Date: 2017-12-07 21:20:55.855630

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
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
        'vld_feature',
        sa.Column('handle', sa.String(length=64), nullable=False),
        sa.Column('date_created', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('handle')
    )
    op.create_table(
        'vld_issue',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('handle', sa.String(length=64), nullable=False),
        sa.Column('changeset_created', sa.BigInteger(), nullable=True),
        sa.Column('changeset_closed', sa.BigInteger(), nullable=True),
        sa.Column('user_created', sa.BigInteger(), nullable=True),
        sa.Column('user_closed', sa.BigInteger(), nullable=True),
        sa.Column('date_created', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('date_closed', sa.DateTime(), nullable=True),
        sa.Column('affected_nodes', postgresql.ARRAY(sa.BigInteger()), nullable=True),
        sa.Column('affected_ways', postgresql.ARRAY(sa.BigInteger()), nullable=True),
        sa.Column('affected_rels', postgresql.ARRAY(sa.BigInteger()), nullable=True),
        sa.ForeignKeyConstraint(['handle'], ['vld_feature.handle'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_vld_issue_handle_affected_nodes', 'vld_issue', ['handle', 'affected_nodes'],
                    unique=False, postgresql_where=sa.text('date_closed IS NOT NULL'))
    op.create_index('ix_vld_issue_handle_affected_rels', 'vld_issue', ['handle', 'affected_rels'],
                    unique=False, postgresql_where=sa.text('date_closed IS NOT NULL'))
    op.create_index('ix_vld_issue_handle_affected_ways', 'vld_issue', ['handle', 'affected_ways'],
                    unique=False, postgresql_where=sa.text('date_closed IS NOT NULL'))
    op.create_index(op.f('ix_vld_issue_user_closed'), 'vld_issue', ['user_closed'], unique=False)
    op.create_index(op.f('ix_vld_issue_user_created'), 'vld_issue', ['user_created'], unique=False)


def downgrade():
    op.drop_index('ix_vld_issue_handle_affected_nodes', table_name='vld_issue')
    op.drop_index('ix_vld_issue_handle_affected_ways', table_name='vld_issue')
    op.drop_index('ix_vld_issue_handle_affected_rels', table_name='vld_issue')
    op.drop_index(op.f('ix_vld_issue_user_created'), table_name='vld_issue')
    op.drop_index(op.f('ix_vld_issue_user_closed'), table_name='vld_issue')
    op.drop_table('vld_issue')
    op.drop_table('vld_feature')
    op.drop_table('vld_state')
    op.drop_table('vld_user')
