# -*- coding: utf-8 -*-

from sqlalchemy.ext.associationproxy import association_proxy
import requests
from urlparse import urlparse, parse_qs
from flask import json, escape

from hgtv.models import db, TimestampMixin, BaseIdNameMixin

from hgtv.models.tag import tags_videos

__all__ = ['ChannelVideo', 'PlaylistVideo', 'Video']


class ChannelVideo(db.Model, TimestampMixin):
    __tablename__ = 'channel_video'
    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'), primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), primary_key=True)
    video = db.relationship('Video', backref=db.backref('_channels', cascade='all, delete-orphan'))
    seq = db.Column(db.Integer, nullable=False)
    relation = db.Column(db.Integer, nullable=False)  # Describes why the channel is linked to the video


class PlaylistVideo(db.Model, TimestampMixin):
    __tablename__ = 'playlist_video'
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.id'), primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), primary_key=True)
    video = db.relationship('Video', backref=db.backref('_playlists', cascade='all, delete-orphan'))
    seq = db.Column(db.Integer, nullable=False)
    description = db.Column(db.UnicodeText, nullable=False, default=True)


class Video(db.Model, BaseIdNameMixin):
    __tablename__ = 'video'
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.id'), nullable=False)
    playlist = db.relationship('Playlist',
        backref=db.backref('primary_videos', cascade='all, delete-orphan'))
    channel = association_proxy('playlist', 'channel')
    description = db.Column(db.UnicodeText, nullable=False, default=u'')
    video_url = db.Column(db.Unicode(250), nullable=False)
    slides_url = db.Column(db.Unicode(250), nullable=False, default=u'')
    thumbnail_url = db.Column(db.Unicode(250), nullable=True, default=u'')

    video_html = db.Column(db.Unicode(250), nullable=False, default=u'')
    slides_html = db.Column(db.Unicode(250), nullable=False, default=u'')

    channels = association_proxy('_channels', 'channel', creator=lambda x: ChannelVideo(channel=x))
    playlists = association_proxy('_playlists', 'playlist', creator=lambda x: PlaylistVideo(playlist=x))

    tags = db.relationship('Tag', secondary=tags_videos, backref=db.backref('videos'))

    def __repr__(self):
        return u'<Video %s>' % self.url_name

    # FIXME: Move these into the view, out of the model
    def process_video(self):
        """
        Get metadata for the video from the corresponding site
        """
        # Parse the video url
        if self.video_url:
            parsed = urlparse(self.video_url)
            # Check video source and get corresponding data
            if parsed.netloc in ['youtube.com', 'www.youtube.com']:
                video_id = parse_qs(parsed.query)['v'][0]
                r = requests.get('https://gdata.youtube.com/feeds/api/videos/%s?v=2&alt=json' % video_id)
                data = json.loads(r.text)
                self.title = data['entry']['title']['$t']
                self.description = escape(data['entry']['media$group']['media$description']['$t'])
                for item in data['entry']['media$group']['media$thumbnail']:
                    if item['yt$name'] == 'mqdefault':
                        self.thumbnail_url = item['url']  # .replace('hqdefault', 'mqdefault')
                self.video_html = '<iframe src="http://www.youtube.com/embed/%s?wmode=transparent&autoplay=1" frameborder="0" allowfullscreen></iframe>' % video_id
            else:
                raise ValueError("Unsupported video site")

    def process_slides(self):
        """
        Get metadata for slides from the corresponding site
        """
        if self.slides_url:
            parsed = urlparse(self.slides_url)
            if parsed.netloc in ['slideshare.net', 'www.slideshare.net']:
                r = requests.get('http://www.slideshare.net/api/oembed/2?url=%s&format=json' % self.slides_url)
                data = json.loads(r.text)
                slides_id = data['slideshow_id']
                self.slides_html = '<iframe src="http://www.slideshare.net/slideshow/embed_code/%s" frameborder="0" marginwidth="0" marginheight="0" scrolling="no"></iframe>' % slides_id
            elif parsed.netloc in ['speakerdeck.com', 'www.speakerdeck.com']:
                r = requests.get('http://speakerdeck.com/oembed.json?url=%s' % self.slides_url)
                data = json.loads(r.text)
                self.slides_html = data['html']
            else:
                self.slides_html = '<iframe src="%s" frameborder="0"></iframe>' % self.slides_url
                raise ValueError("Unsupported slides site")
