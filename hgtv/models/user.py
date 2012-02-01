# -*- coding: utf-8 -*-

from flask import g
from flask.ext.lastuser.sqlalchemy import UserBase
from hgtv.models import db

__all__ = ['User']

class User(db.Model, UserBase):
    __tablename__ = 'user'

def default_user(context):
    return g.user.id if g.user else None
