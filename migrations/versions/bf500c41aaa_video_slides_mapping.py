"""video_slides_mapping_json

Revision ID: bf500c41aaa
Revises: 2f19c3127125
Create Date: 2013-03-11 17:51:39.927784

"""

# revision identifiers, used by Alembic.
revision = 'bf500c41aaa'
down_revision = '2f19c3127125'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column("video", sa.Column('video_slides_mapping_json', sa.UnicodeText, nullable=True))


def downgrade():
    op.drop_column("video", "video_slides_mapping_json")
