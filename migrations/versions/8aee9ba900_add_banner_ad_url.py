"""add banner_ad_url

Revision ID: 8aee9ba900
Revises: 105357c43661
Create Date: 2013-02-24 17:01:45.003494

"""

# revision identifiers, used by Alembic.
revision = '8aee9ba900'
down_revision = '105357c43661'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column("playlist", sa.Column('banner_ad_url', sa.Unicode(250), nullable=True))


def downgrade():
    op.drop_column("playlist", "banner_ad_url")
