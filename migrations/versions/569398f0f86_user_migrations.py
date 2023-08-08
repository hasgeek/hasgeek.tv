"""User migrations

Revision ID: 569398f0f86
Revises: 313a997eef03
Create Date: 2014-03-08 23:50:10.626701

"""

# revision identifiers, used by Alembic.
revision = '569398f0f86'
down_revision = '313a997eef03'

import sqlalchemy as sa
from alembic import op


def upgrade():
    op.add_column(
        'channel',
        sa.Column('status', sa.Integer(), nullable=False, server_default=sa.text('0')),
    )
    op.add_column(
        'user',
        sa.Column('status', sa.Integer(), nullable=False, server_default=sa.text('0')),
    )
    op.alter_column('channel', 'status', server_default=None)
    op.alter_column('user', 'status', server_default=None)


def downgrade():
    op.drop_column('user', 'status')
    op.drop_column('channel', 'status')
