"""create user table

Revision ID: b95b832cb0c4
Revises:
Create Date: 2017-10-09 01:54:26.674733

"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = 'b95b832cb0c4'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'user',
        sa.Column('osm_uid', sa.Integer, primary_key=True),
        sa.Column('osm_user', sa.String(50), nullable=False),
    )


def downgrade():
    op.drop_table('user')
