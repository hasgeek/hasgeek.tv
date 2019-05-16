"""Switch to timestamptz

Revision ID: d5f66cf4ec40
Revises: a0b972b22658
Create Date: 2019-05-10 21:42:10.439540

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd5f66cf4ec40'
down_revision = 'a0b972b22658'
branch_labels = None
depends_on = None

migrate_table_columns = [
    ('channel', 'created_at'),
    ('channel', 'updated_at'),
    ('playlist', 'created_at'),
    ('playlist', 'updated_at'),
    ('playlist_redirect', 'created_at'),
    ('playlist_redirect', 'updated_at'),
    ('playlist_video', 'created_at'),
    ('playlist_video', 'updated_at'),
    ('tag', 'created_at'),
    ('tag', 'updated_at'),
    ('user', 'created_at'),
    ('user', 'updated_at'),
    ('video', 'created_at'),
    ('video', 'updated_at'),
    ]


def upgrade():
    for table, column in migrate_table_columns:
        op.execute(sa.DDL(
            'ALTER TABLE "%(table)s" ALTER COLUMN "%(column)s" TYPE TIMESTAMP WITH TIME ZONE USING "%(column)s" AT TIME ZONE \'UTC\'',
            context={'table': table, 'column': column}
            ))


def downgrade():
    for table, column in reversed(migrate_table_columns):
        op.execute(sa.DDL(
            'ALTER TABLE "%(table)s" ALTER COLUMN "%(column)s" TYPE TIMESTAMP WITHOUT TIME ZONE',
            context={'table': table, 'column': column}
            ))
