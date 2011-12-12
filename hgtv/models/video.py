#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

from hgtv.models import db, BaseMixin
from hgtv.models.tag import tags_videos

__all__ = ['Video']

class Video(db.Model, BaseMixin):
    __tablename__ = 'video'
    name = db.Column(db.Unicode(80), unique=True, nullable=False)
    title = db.Column(db.Unicode(80), unique=True, nullable=False)
    description = db.Column(db.Text(), nullable=False)
    url = db.Column(db.Unicode(80), unique=True, nullable=False)
    season_id = db.Column(db.Integer, db.ForeignKey('season.id'), nullable=False)

    tags = db.relationship('Tag', secondary=tags_videos, backref=db.backref('videos'))
