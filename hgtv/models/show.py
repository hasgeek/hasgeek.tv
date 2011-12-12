#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

from hgtv.models import db, BaseMixin

__all__ = ['Show']

class Show(db.Model, BaseMixin):
    __tablename__ = 'show'
    name = db.Column(db.Unicode(80), unique=True, nullable=False)
    title = db.Column(db.Unicode(80), unique=True, nullable=False)
    description = db.Column(db.Text(), nullable=False)

    seasons = db.relationship('Season', backref='show')
