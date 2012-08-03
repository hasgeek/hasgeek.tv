# -*- coding: utf-8 -*-

from sqlalchemy.ext.associationproxy import association_proxy

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

    # FIXME: Use proper urlparse library and contsruct the url
    def embed_for(self, action='view'):
        video_html = self.video_html
        if action == 'edit':
            edit_video_html = video_html.replace("autoplay=1", "autoplay=0")
            return edit_video_html
        else:
            return video_html