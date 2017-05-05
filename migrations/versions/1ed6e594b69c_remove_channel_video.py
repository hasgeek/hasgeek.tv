"""remove channel_video Table

Revision ID: 1ed6e594b69c
Revises: 569460636548
Create Date: 2013-07-06 01:44:54.691621

"""

# revision identifiers, used by Alembic.
revision = '1ed6e594b69c'
down_revision = '569460636548'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.drop_table("channel_video")


def downgrade():
    op.create_table("channel_video",
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
        sa.Column("channel_id", sa.Integer, nullable=False),
        sa.Column("video_id", sa.Integer, nullable=False),
        sa.Column("seq", sa.Integer, nullable=False),
        sa.Column("relation", sa.Integer, nullable=False))
    op.create_foreign_key("channel_video_video_id_fkey", "channel_video", "channel", "channel_id", "id")
    op.create_foreign_key("channel_video_channel_id_fkey", "channel_video", "video", "video_id", "id")
