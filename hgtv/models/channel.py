# -*- coding: utf-8 -*-

from datetime import date

from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.ext.associationproxy import association_proxy

from hgtv.models import db, BaseNameMixin
from hgtv.models.video import ChannelVideo, PlaylistVideo


__all__ = ['CHANNEL_TYPE', 'PLAYLIST_TYPE', 'Channel', 'Playlist']


class CHANNEL_TYPE:
    UNDEFINED = 0
    PERSON = 1
    ORGANIZATION = 2
    EVENTSERIES = 3


class PLAYLIST_TYPE:
    REGULAR = 0
    EVENT = 1
    WATCHED = 2
    ATTENDED = 3


channel_types = {
    0: u"Channel",
    1: u"Person",
    2: u"Organization",
    3: u"Event Series",
    }


playlist_types = {
    0: u"Playlist",
    1: u"Event",
    }


class Channel(BaseNameMixin, db.Model):
    __tablename__ = 'channel'
    userid = db.Column(db.Unicode(22), nullable=False, unique=True)
    description = db.Column(db.UnicodeText, default=u'', nullable=False)
    featured = db.Column(db.Boolean, default=False, nullable=False)
    type = db.Column(db.Integer, default=CHANNEL_TYPE.UNDEFINED, nullable=False)

    _videos = db.relationship(ChannelVideo,
        order_by=[ChannelVideo.seq],
        collection_class=ordering_list('seq'),
        backref='channel',
        cascade='all, delete-orphan')
    videos = association_proxy('_videos', 'video', creator=lambda x: ChannelVideo(video=x))

    def type_label(self):
        return channel_types.get(self.type, channel_types[0])


class Playlist(BaseNameMixin, db.Model):
    __tablename__ = 'playlist'
    short_title = db.Column(db.Unicode(80), nullable=False, default=u'')
    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'), nullable=False)
    channel = db.relationship(Channel, primaryjoin=channel_id == Channel.id,
        backref=db.backref('playlists', cascade='all, delete-orphan'))
    description = db.Column(db.UnicodeText, default=u'', nullable=False)
    recorded_date = db.Column(db.Date, nullable=True)
    published_date = db.Column(db.Date, nullable=False, default=date.today)
    featured = db.Column(db.Boolean, default=False, nullable=False)
    type = db.Column(db.Integer, default=PLAYLIST_TYPE.REGULAR, nullable=False)

    _videos = db.relationship(PlaylistVideo,
        order_by=[PlaylistVideo.seq],
        collection_class=ordering_list('seq'),
        backref='playlist',
        cascade='all, delete-orphan')
    videos = association_proxy('_videos', 'video', creator=lambda x: PlaylistVideo(video=x))

    def type_label(self):
        return playlist_types.get(self.type, playlist_types[0])
