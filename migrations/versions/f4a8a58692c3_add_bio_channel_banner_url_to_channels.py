"""add_bio_channel_banner_url_to_channels

Revision ID: f4a8a58692c3
Revises: 569398f0f86
Create Date: 2017-10-03 18:50:13.049295

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'f4a8a58692c3'
down_revision = '569398f0f86'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('channel', sa.Column('bio', sa.Unicode(length=250), nullable=True))
    op.add_column(
        'channel',
        sa.Column('channel_banner_url', sa.Unicode(length=250), nullable=True),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('channel', 'channel_banner_url')
    op.drop_column('channel', 'bio')
    # ### end Alembic commands ###
