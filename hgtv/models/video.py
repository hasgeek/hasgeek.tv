#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

from hgtv.models import db, BaseNameMixin
from hgtv.models.tag import tags_videos, Tag
from hgtv.models.channel import Channel, channels_videos, playlists_videos
import requests
import re
from urlparse import urlparse, parse_qs
import json


__all__ = ['Video']


class Video(db.Model, BaseNameMixin):
    __tablename__ = 'video'
    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'), nullable=False)
    channel = db.relationship(Channel, primaryjoin=channel_id == Channel.id,
        backref=db.backref('videos', cascade='all, delete-orphan'))
    description = db.Column(db.UnicodeText, nullable=False, default=u'')
    url = db.Column(db.Unicode(250), nullable=False)
    slides = db.Column(db.Unicode(250), nullable=False, default=u'')
    thumbnail_url = db.Column(db.Unicode(250), nullable=True, default=u'')

    tags = db.relationship('Tag', secondary=tags_videos, backref=db.backref('videos'))
    channels = db.relationship('Channel', secondary=channels_videos, backref=db.backref('tagged_videos'))
    playlists = db.relationship('Playlist', secondary=playlists_videos, backref=db.backref('videos'))

    def __repr__(self):
        return u'<Video %s>' % self.name

    def get_metadata(self):
        """
        Get Metadata for the video from the corresponding site
        """
        # Parse the video url
        if self.url:
            parsed = urlparse(self.url)
        else:
            return None
        # Check video source and get corresponding data
        if parsed.netloc == 'youtube.com' or 'www.youtube.com':
            self.get_youtube_data(parsed)

    def get_youtube_data(self, parsed):
        """
        Get Metadata from youtube
        """
        video = parse_qs(parsed.query)['v'][0]
        r = requests.get('https://gdata.youtube.com/feeds/api/videos/%s?v=2&alt=json' % video)
        data = json.loads(r.text)
        self.title = data['entry']['title']['$t']
        self.description = data['entry']['media$group']['media$description']['$t']
        for item in data['entry']['media$group']['media$thumbnail']:
            if item['yt$name'] == 'hqdefault':
                self.thumbnail_url = item['url']
        for item in data['entry']['category']:
            if item['scheme'] == 'http://gdata.youtube.com/schemas/2007/keywords.cat':
                Tag.get(item['term'])
