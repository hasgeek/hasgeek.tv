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

    def get_auto_playlist(self, auto_type, create=False):
        playlist = Playlist.query.filter_by(channel=self.channel, auto_type=auto_type).first()
        if playlist is None and create:
            playlist = Playlist(channel=self.channel,
                type=auto_type,
                title=playlist_auto_types.get(auto_type),
                public=False)  # Automatic playlists are hidden by default
            db.session.add(playlist)
        return playlist

    def auto_playlists(self):
        """
        Returns a dictionary of playlist_code: playlist
        """
        return dict((playlist.auto_type, playlist) for playlist in Playlist.query.filter_by(
            channel=self.channel).filter(Playlist.auto_type is not None))

    def playlist_for_watched(self, create=False):
        return self.get_auto_playlist(PLAYLIST_AUTO_TYPE.WATCHED, create)

    def playlist_for_liked(self, create=False):
        return self.get_auto_playlist(PLAYLIST_AUTO_TYPE.LIKED, create)

    def playlist_for_disliked(self, create=False):
        return self.get_auto_playlist(PLAYLIST_AUTO_TYPE.DISLIKED, create)

    def playlist_for_speaking_in(self, create=False):
        return self.get_auto_playlist(PLAYLIST_AUTO_TYPE.SPEAKING_IN, create)

    def playlist_for_appearing_in(self, create=False):
        return self.get_auto_playlist(PLAYLIST_AUTO_TYPE.APPEARING_IN, create)

    def playlist_for_crew_in(self, create=False):
        return self.get_auto_playlist(PLAYLIST_AUTO_TYPE.CREW_IN, create)

    def playlist_for_starred(self, create=False):
        return self.get_auto_playlist(PLAYLIST_AUTO_TYPE.STARRED, create)


def default_user(context):
    return g.user.id if g.user else None
