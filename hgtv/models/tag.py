# -*- coding: utf-8 -*-

from coaster import makename
from hgtv.models import db, BaseMixin

__all__ = ['Tag']

class Tag(db.Model, BaseMixin):
    __tablename__ = 'tag'
    name = db.Column(db.Unicode(80), unique=True, nullable=False)
    title = db.Column(db.Unicode(80), unique=True, nullable=False)
    
    @classmethod
    def get(cls, title):
        tag = cls.query.filter_by(title=title).first()
        if tag:
            return tag
        else:
            name = makename(title)
            # Is this name already in use? If yes, return it
            tag = cls.query.filter_by(name=name).first()
            if tag:
                return tag
            else:
                tag = cls(name=name, title=title)
                db.session.add(tag)
                return tag

    def rename(self, title):
        name = makename(tagname)
        if self.query.filter_by(name=name).first() is not None:
            raise ValueError, u"Name already in use"
        else:
            self.name = name
            self.title = title

tags = db.Table('tags_videos',
        db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
        db.COlumn('video_id', db.Integer, db.ForeignKey('video.id'))
    )
