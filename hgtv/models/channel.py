# -*- coding: utf-8 -*-

from hgtv.models import db, BaseNameMixin


class Channel(db.Model, BaseNameMixin):
    __tablename__ = 'channel'
    userid = db.Column(db.Unicode(22), nullable=False, unique=True)
    featured = db.Column(db.Boolean, default=False, nullable=False)


class Playlist(db.Model, BaseNameMixin):
    __tablename__ = 'playlist'
    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'), nullable=False)
    channel = db.relationship(Channel, primaryjoin=channel_id == Channel.id,
        backref=db.backref('playlists', cascade='all, delete-orphan'))
    featured = db.Column(db.Boolean, default=False, nullable=False)


channels_videos = db.Table('channels_videos',
    db.Column('channel_id', db.Integer, db.ForeignKey('channel.id'), nullable=False),
    db.Column('video_id', db.Integer, db.ForeignKey('video.id'), nullable=False)
    )


playlists_videos = db.Table('playlists_videos',
    db.Column('playlist_id', db.Integer, db.ForeignKey('playlist.id'), nullable=False),
    db.Column('video_id', db.Integer, db.ForeignKey('video.id'), nullable=False)
    )
