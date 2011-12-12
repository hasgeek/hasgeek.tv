#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

from hgtv.models import db, BaseMixin

__all__ = ['Season']

class Season(db.Model, BaseMixin):
    __tablename__ = 'season'
    name = db.Column(db.Unicode(80), unique=True, nullable=False)
    title = db.Column(db.Unicode(80), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    show_id = db.Column(db.Integer, db.ForeignKey('show.id'))

    videos = db.relationship('Video', backref='season')
