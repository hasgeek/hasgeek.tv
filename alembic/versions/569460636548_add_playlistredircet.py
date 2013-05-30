"""Add PlaylistRedircet

Revision ID: 569460636548
Revises: bf500c41aaa
Create Date: 2013-05-30 12:50:15.831765

"""

# revision identifiers, used by Alembic.
revision = '569460636548'
down_revision = 'bf500c41aaa'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'playlist_redirect',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('channel_id', sa.Integer, nullable=False),
        sa.Column('name', sa.Unicode(250), nullable=False),
        sa.Column('playlist_id', sa.Integer, nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False))
    op.create_foreign_key("fk_playlist_redirect_playlist_id", "playlist_redirect", "playlist", ["playlist_id"], ["id"])


def downgrade():
    op.drop_table('playlist_redirect')
    op.drop_constraint("fk_playlist_redirect_playlist_id")
