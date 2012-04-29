# -*- coding: utf-8 -*-

from flask import g, url_for
from flask.ext.lastuser.sqlalchemy import UserBase
from hgtv.models import db
from hgtv.models.channel import Channel

__all__ = ['User']


class User(db.Model, UserBase):
    __tablename__ = 'user'

    @property
    def profile_url(self):
        return url_for('channel_view', channel=self.username or self.userid)

    @property
    def channel(self):
        return Channel.query.filter_by(userid=self.userid).first()

    @property
    def channels(self):
        return Channel.query.filter(Channel.userid.in_(self.user_organization_ids())).all()


def default_user(context):
    return g.user.id if g.user else None
