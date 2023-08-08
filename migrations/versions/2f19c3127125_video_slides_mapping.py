"""video_slides_mapping

Revision ID: 2f19c3127125
Revises: 8aee9ba900
Create Date: 2013-03-07 22:21:13.248411

"""

# revision identifiers, used by Alembic.
revision = '2f19c3127125'
down_revision = '8aee9ba900'

import sqlalchemy as sa
from alembic import op


def upgrade():
    op.add_column(
        "video", sa.Column('video_slides_mapping', sa.UnicodeText, nullable=True)
    )


def downgrade():
    op.drop_column("video", "video_slides_mapping")
