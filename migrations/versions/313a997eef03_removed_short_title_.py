"""Removed short_title column

Revision ID: 313a997eef03
Revises: 1ed6e594b69c
Create Date: 2013-09-06 11:13:48.325107

"""

# revision identifiers, used by Alembic.
revision = '313a997eef03'
down_revision = '1ed6e594b69c'

import sqlalchemy as sa

from alembic import op


def upgrade():
    op.drop_column('playlist', 'short_title')


def downgrade():
    op.add_column(
        'playlist',
        sa.Column(
            'short_title', sa.Unicode(80), nullable=False, server_default=sa.text("''")
        ),
    )
