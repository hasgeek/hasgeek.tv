"""Remove unused commentease integration

Revision ID: 81c6a670d47d
Revises: f4a8a58692c3
Create Date: 2019-05-10 17:04:17.387766

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '81c6a670d47d'
down_revision = 'f4a8a58692c3'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint(u'video_comments_id_fkey', 'video', type_='foreignkey')
    op.drop_column('video', 'allow_commenting')
    op.drop_column('video', 'comments_id')
    op.drop_table('comment_tree')
    op.drop_table('comment')
    op.drop_table('commentset')
    op.drop_table('commentspace')
    op.drop_table('vote')
    op.drop_table('voteset')
    op.drop_table('votespace')


def downgrade():
    op.create_table('votespace',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
        sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
        sa.Column('type', sa.VARCHAR(length=4), autoincrement=False, nullable=True),
        sa.Column('count', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('downvoting', sa.BOOLEAN(), autoincrement=False, nullable=False),
        sa.PrimaryKeyConstraint('id', name=u'votespace_pkey')
        )
    op.create_table('voteset',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
        sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
        sa.Column('type', sa.VARCHAR(length=4), autoincrement=False, nullable=True),
        sa.Column('count', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('score', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('pattern', sa.SMALLINT(), autoincrement=False, nullable=False),
        sa.Column('min', sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column('max', sa.INTEGER(), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint('id', name=u'voteset_pkey')
        )
    op.create_table('vote',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
        sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
        sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('votespace_id', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('votedown', sa.BOOLEAN(), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(['user_id'], [u'user.id'], name=u'vote_user_id_fkey'),
        sa.ForeignKeyConstraint(['votespace_id'], [u'votespace.id'], name=u'vote_votespace_id_fkey'),
        sa.PrimaryKeyConstraint('id', name=u'vote_pkey'),
        sa.UniqueConstraint('user_id', 'votespace_id', name=u'vote_user_id_votespace_id_key')
        )
    op.create_table('commentspace',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
        sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
        sa.Column('type', sa.VARCHAR(length=4), autoincrement=False, nullable=True),
        sa.Column('count', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('downvoting', sa.BOOLEAN(), autoincrement=False, nullable=False),
        sa.PrimaryKeyConstraint('id', name=u'commentspace_pkey')
        )
    op.create_table('commentset',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
        sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
        sa.Column('type', sa.VARCHAR(length=4), autoincrement=False, nullable=True),
        sa.Column('count', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('count_toplevel', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('count_replies', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('downvoting', sa.BOOLEAN(), autoincrement=False, nullable=False),
        sa.PrimaryKeyConstraint('id', name=u'commentset_pkey')
        )
    op.create_table('comment',
        sa.Column('id', sa.INTEGER(), server_default=sa.text(u"nextval('comment_id_seq'::regclass)"), autoincrement=True, nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
        sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
        sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column('commentspace_id', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('reply_to_id', sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column('parser', sa.VARCHAR(length=10), autoincrement=False, nullable=False),
        sa.Column('message', sa.TEXT(), autoincrement=False, nullable=False),
        sa.Column('message_html', sa.TEXT(), autoincrement=False, nullable=False),
        sa.Column('status', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('votes_id', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('edited_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(['commentspace_id'], [u'commentspace.id'], name=u'comment_commentspace_id_fkey'),
        sa.ForeignKeyConstraint(['reply_to_id'], [u'comment.id'], name=u'comment_reply_to_id_fkey'),
        sa.ForeignKeyConstraint(['user_id'], [u'user.id'], name=u'comment_user_id_fkey'),
        sa.ForeignKeyConstraint(['votes_id'], [u'votespace.id'], name=u'comment_votes_id_fkey'),
        sa.PrimaryKeyConstraint('id', name=u'comment_pkey'),
        postgresql_ignore_search_path=False
        )
    op.create_table('comment_tree',
        sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
        sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
        sa.Column('parent_id', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('child_id', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('depth', sa.SMALLINT(), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(['child_id'], [u'comment.id'], name=u'comment_tree_child_id_fkey'),
        sa.ForeignKeyConstraint(['parent_id'], [u'comment.id'], name=u'comment_tree_parent_id_fkey'),
        sa.PrimaryKeyConstraint('parent_id', 'child_id', name=u'comment_tree_pkey')
        )
    op.add_column('video', sa.Column('allow_commenting', sa.BOOLEAN(), autoincrement=False, nullable=False,
        server_default=sa.sql.expression.false()))
    op.alter_column('video', 'allow_commenting', server_default=None)
    op.add_column('video', sa.Column('comments_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key(u'video_comments_id_fkey', 'video', 'commentspace', ['comments_id'], ['id'])
