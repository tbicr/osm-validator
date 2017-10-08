"""create user table

Revision ID: 2de2757482a9
Revises: 
Create Date: 2017-10-08 18:25:36.139394

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2de2757482a9'
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
