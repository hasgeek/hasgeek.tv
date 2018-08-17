# -*- coding: utf-8 -*-

from flask import g, url_for
from werkzeug import cached_property
from flask_lastuser.sqlalchemy import UserBase2

from hgtv.models import db
from hgtv.models.channel import Channel

__all__ = ['User']


class User(UserBase2, db.Model):
    __tablename__ = 'user'

    autoplay = db.Column(db.Boolean, default=True, nullable=False)

    @cached_property
    def profile_url(self):
        return url_for('channel_view', channel=self.username or self.userid)

    @cached_property
    def channel(self):
        return Channel.query.filter_by(userid=self.userid).first()

    @cached_property
    def channels(self):
        # Join lists so that the user's personal channel is always the first
        return [self.channel] + Channel.query.filter(
            Channel.userid.in_(self.organizations_owned_ids())).order_by('title').all()

    def organization_links(self):
        return [{'link': url_for('channel_view', channel=org['name']),
                 'title': org['title']} for org in self.organizations_memberof()]

    def get_video_preference(self, video):
        starred_playlist = self.channel.playlist_for_starred()
        queue_playlist = self.channel.playlist_for_queue()
        liked_playlist = self.channel.playlist_for_liked()
        disliked_playlist = self.channel.playlist_for_disliked()
        video_flags = {
            'starred': True if starred_playlist and video in starred_playlist.videos else False,
            'queued': True if queue_playlist and video in queue_playlist.videos else False,
            'liked': True if liked_playlist and video in liked_playlist.videos else False,
            'disliked': True if disliked_playlist and video in disliked_playlist.videos else False
        }
        return video_flags


def default_user(context):
    return g.user.id if g.user else None
