# -*- coding: utf-8 -*-

from flask import g, url_for
from flask.ext.lastuser.sqlalchemy import UserBase
from hgtv.models import db
from hgtv.models.channel import Channel, Playlist, PLAYLIST_TYPE

__all__ = ['User']


class User(db.Model, UserBase):
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

    def get_or_create_playlist(self, playlist_type):
        playlist = Playlist.query.filter_by(channel=self.channel, type=playlist_type).first()
        if playlist is None:
            playlist = Playlist(channel=self.channel, type=playlist_type)
            db.session.add(playlist)
        return playlist

    def playlist_for_watched(self):
        return self.get_or_create_playlist(PLAYLIST_TYPE.WATCHED)

    def playlist_for_liked(self):
        return self.get_or_create_playlist(PLAYLIST_TYPE.LIKED)

    def playlist_for_disliked(self):
        return self.get_or_create_playlist(PLAYLIST_TYPE.DISLIKED)

    def playlist_for_speaking_in(self):
        return self.get_or_create_playlist(PLAYLIST_TYPE.SPEAKING_IN)

    def playlist_for_appearing_in(self):
        return self.get_or_create_playlist(PLAYLIST_TYPE.APPEARING_IN)

    def playlist_for_crew_in(self):
        return self.get_or_create_playlist(PLAYLIST_TYPE.CREW_IN)


def default_user(context):
    return g.user.id if g.user else None
