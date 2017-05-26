"""Add a featured column to video table

Revision ID: 20629a2e2409
Revises: 1ed6e594b69c
Create Date: 2013-07-09 22:52:56.487246

"""

# revision identifiers, used by Alembic.
revision = '20629a2e2409'
down_revision = '1ed6e594b69c'

from alembic import op
import sqlalchemy as sa


def upgrade():
    #featured = db.Column(db.Boolean, default=False, nullable=False)
    op.add_column("video", sa.Column("featured", sa.Boolean, nullable=False, server_default=sa.DefaultClause("False")))
    op.alter_column("video", "featured", server_default=None)


def downgrade():
    op.drop_column("video", "featured")
