# -*- coding: utf-8 -*-

from flask import g, url_for
from flask.ext.lastuser.sqlalchemy import UserBase
from hgtv.models import db
from hgtv.models.channel import Channel, Playlist, PLAYLIST_AUTO_TYPE, playlist_auto_types

__all__ = ['User']


class User(UserBase, db.Model):
    __tablename__ = 'user'

    autoplay = db.Column(db.Boolean, default=True, nullable=False)

    @property
    def profile_url(self):
        return url_for('channel_view', channel=self.username or self.userid)

    @property
    def channel(self):
        return Channel.query.filter_by(userid=self.userid).first()

    @property
    def channels(self):
        # Join lists so that the user's personal channel is always the first
        return [self.channel] + Channel.query.filter(
            Channel.userid.in_(self.organizations_owned_ids())).order_by('title').all()


def default_user(context):
    return g.user.id if g.user else None
