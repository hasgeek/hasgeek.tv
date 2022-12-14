"""Add channel_logo column in channel table

Revision ID: 473c78e7d626
Revises: None
Create Date: 2013-02-16 20:36:15.877175

"""

# revision identifiers, used by Alembic.
revision = '473c78e7d626'
down_revision = None

import sqlalchemy as sa

from alembic import op


def upgrade():
    op.add_column(
        "channel", sa.Column('channel_logo_filename', sa.Unicode(250), nullable=True)
    )


def downgrade():
    op.drop_column("channel", "channel_logo_filename")
