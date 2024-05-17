from coaster.utils import make_name

from . import BaseMixin, Model, db, sa, sa_orm

__all__ = ['Tag']


class Tag(BaseMixin, Model):
    __tablename__ = 'tag'
    name = sa_orm.mapped_column(sa.Unicode(80), unique=True, nullable=False)
    title = sa_orm.mapped_column(sa.Unicode(80), unique=True, nullable=False)

    def __repr__(self):
        return self.name

    @classmethod
    def get(cls, title):
        tag = cls.query.filter_by(title=title).first()
        if tag:
            return tag
        else:
            name = make_name(title)
            # Is this name already in use? If yes, return it
            tag = cls.query.filter_by(name=name).first()
            if tag:
                return tag
            else:
                tag = cls(name=name, title=title)
                db.session.add(tag)
                return tag

    def rename(self, title):
        name = make_name(title)
        if self.query.filter_by(name=name).first() is not None:
            raise ValueError("Name already in use")
        else:
            self.name = name
            self.title = title


tags_videos = sa.Table(
    'tags_videos',
    Model.metadata,
    sa.Column('tag_id', sa.Integer, sa.ForeignKey('tag.id')),
    sa.Column('video_id', sa.Integer, sa.ForeignKey('video.id')),
)
