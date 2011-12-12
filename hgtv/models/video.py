#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

from hgtv.models import db, BaseMixin

__all__ = ['Video']

class Video(db.Model, BaseMixin):
    __tablename__ = 'video'
    name = db.Column(db.Unicode(80), unique=True, nullable=False)
    title = db.Column(db.Unicode(80), unique=True, nullable=False)
    description = db.Column(db.Text(), nullable=False)
    url = db.Column(db.Unicode(80), unique=True, nullable=False)
    season_id = db.Column(db.Integer, db.ForeignKey('season.id'))

    tags = db.relationship('Tag', backref=db.backref('videos'))
