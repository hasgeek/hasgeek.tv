"""Add banner_ad column in playlist table

Revision ID: 105357c43661
Revises: 473c78e7d626
Create Date: 2013-02-24 12:00:01.521676

"""

# revision identifiers, used by Alembic.
revision = '105357c43661'
down_revision = '473c78e7d626'

import sqlalchemy as sa
from alembic import op


def upgrade():
    op.add_column(
        "playlist", sa.Column('banner_ad_filename', sa.Unicode(250), nullable=True)
    )


def downgrade():
    op.drop_column("playlist", "banner_ad_filename")
