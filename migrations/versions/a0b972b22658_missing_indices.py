"""Missing indices

Revision ID: a0b972b22658
Revises: 81c6a670d47d
Create Date: 2019-05-10 17:16:41.209524

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'a0b972b22658'
down_revision = '81c6a670d47d'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint('playlist_name_key', 'playlist', type_='unique')
    op.create_unique_constraint(
        'playlist_channel_id_name_key', 'playlist', ['channel_id', 'name']
    )

    op.create_unique_constraint(
        'playlist_redirect_channel_id_name_key',
        'playlist_redirect',
        ['channel_id', 'name'],
    )
    op.create_foreign_key(
        'playlist_redirect_channel_id_fkey',
        'playlist_redirect',
        'channel',
        ['channel_id'],
        ['id'],
    )

    op.drop_constraint(
        'fk_playlist_redirect_playlist_id', 'playlist_redirect', type_='foreignkey'
    )
    op.create_foreign_key(
        'playlist_redirect_playlist_id_fkey',
        'playlist_redirect',
        'playlist',
        ['playlist_id'],
        ['id'],
    )

    op.create_check_constraint('channel_name_check', 'channel', sa.text("name <> ''"))
    op.create_check_constraint('playlist_name_check', 'playlist', sa.text("name <> ''"))
    op.create_check_constraint('video_name_check', 'video', sa.text("name <> ''"))

    op.alter_column(
        'user',
        'userinfo',
        type_=sa.dialects.postgresql.JSONB,
        postgresql_using='"userinfo"::jsonb',
    )


def downgrade():
    op.alter_column(
        'user',
        'userinfo',
        type_=sa.dialects.postgresql.JSON,
        postgresql_using='"userinfo"::json',
    )

    op.drop_constraint('video_name_check', 'video', type_='check')
    op.drop_constraint('playlist_name_check', 'playlist', type_='check')
    op.drop_constraint('channel_name_check', 'channel', type_='check')

    op.drop_constraint(
        'playlist_redirect_playlist_id_fkey', 'playlist_redirect', type_='foreignkey'
    )
    op.create_foreign_key(
        'fk_playlist_redirect_playlist_id',
        'playlist_redirect',
        'playlist',
        ['playlist_id'],
        ['id'],
    )

    op.drop_constraint(
        'playlist_redirect_channel_id_fkey', 'playlist_redirect', type_='foreignkey'
    )
    op.drop_constraint(
        'playlist_redirect_channel_id_name_key', 'playlist_redirect', type_='unique'
    )

    op.drop_constraint('playlist_channel_id_name_key', 'playlist', type_='unique')
    op.create_unique_constraint('playlist_name_key', 'playlist', ['channel_id', 'name'])
