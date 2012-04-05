#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

from hgtv.models import db, BaseNameMixin
from hgtv.models.tag import tags_videos
from hgtv.models.channel import Channel, channels_videos, playlists_videos

__all__ = ['Video']


class Video(db.Model, BaseNameMixin):
    __tablename__ = 'video'
    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'), nullable=False)
    channel = db.relationship(Channel, primaryjoin=channel_id == Channel.id,
        backref=db.backref('videos', cascade='all, delete-orphan'))
    description = db.Column(db.UnicodeText, nullable=False, default=u'')
    url = db.Column(db.Unicode(250), nullable=False)
    slides = db.Column(db.Unicode(250), nullable=False, default=u'')

    tags = db.relationship('Tag', secondary=tags_videos, backref=db.backref('videos'))
    channels = db.relationship('Channel', secondary=channels_videos, backref=db.backref('tagged_videos'))
    playlists = db.relationship('Playlist', secondary=playlists_videos, backref=db.backref('videos'))

    def __repr__(self):
        return u'<Video %s>' % self.name
