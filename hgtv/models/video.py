# -*- coding: utf-8 -*-

from sqlalchemy.ext.associationproxy import association_proxy
from flask import Markup, url_for
from flask.ext.commentease import CommentingMixin
from hgtv.models import db, TimestampMixin, BaseIdNameMixin
from hgtv.models.tag import tags_videos

__all__ = ['ChannelVideo', 'PlaylistVideo', 'Video']


class ChannelVideo(TimestampMixin, db.Model):
    __tablename__ = 'channel_video'
    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'), primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), primary_key=True)
    video = db.relationship('Video', backref=db.backref('_channels', cascade='all, delete-orphan'))
    seq = db.Column(db.Integer, nullable=False)
    relation = db.Column(db.Integer, nullable=False)  # Describes why the channel is linked to the video


class PlaylistVideo(TimestampMixin, db.Model):
    __tablename__ = 'playlist_video'
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.id'), primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), primary_key=True)
    video = db.relationship('Video', backref=db.backref('_playlists', cascade='all, delete-orphan'))
    seq = db.Column(db.Integer, nullable=False)
    description = db.Column(db.UnicodeText, nullable=False, default=True)


class Video(BaseIdNameMixin, CommentingMixin, db.Model):
    __tablename__ = 'video'
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.id'), nullable=False)
    playlist = db.relationship('Playlist',
        backref=db.backref('primary_videos', cascade='all, delete-orphan'))
    channel = association_proxy('playlist', 'channel')
    description = db.Column(db.UnicodeText, nullable=False, default=u'')
    video_url = db.Column(db.Unicode(250), nullable=False)
    slides_url = db.Column(db.Unicode(250), nullable=False, default=u'')
    thumbnail_url = db.Column(db.Unicode(250), nullable=True, default=u'')

    video_source = db.Column(db.Unicode(80), nullable=False, default=u'')
    video_sourceid = db.Column(db.Unicode(80), nullable=False, default=u'')

    slides_source = db.Column(db.Unicode(80), nullable=False, default=u'')
    slides_sourceid = db.Column(db.Unicode(80), nullable=False, default=u'')

    channels = association_proxy('_channels', 'channel', creator=lambda x: ChannelVideo(channel=x))
    playlists = association_proxy('_playlists', 'playlist', creator=lambda x: PlaylistVideo(playlist=x))

    tags = db.relationship('Tag', secondary=tags_videos, backref=db.backref('videos'))

    def __repr__(self):
        return u'<Video %s>' % self.url_name

    def permissions(self, user, inherited=None):
        perms = super(Video, self).permissions(user, inherited)
        perms.add('view')
        if user and self.channel.userid in user.user_organizations_owned_ids():
            perms.add('edit')
            perms.add('delete')
        else:
            if 'edit' in perms:
                perms.remove('edit')
            if 'delete' in perms:
                perms.remove('delete')
        return perms

    def url_for(self, action='view', channel=None, playlist=None, _external=False):
        channel = channel or self.channel
        playlist = playlist or self.playlist
        if playlist.channel != channel or playlist not in self.playlists:
            return
        if action == 'view':
            return url_for('video_view',
                channel=channel.name, playlist=playlist.name,
                video=self.url_name, _external=_external)
        elif action == 'remove-video':
            return url_for('video_remove',
                channel=channel.name, playlist=playlist.name,
                video=self.url_name, _external=_external)
        # Edit and Delete can only be from the source playlist
        elif action == 'edit':
            return url_for('video_edit',
                channel=self.channel.name, playlist=self.playlist.name,
                video=self.url_name, _external=_external)
        elif action == 'delete':
            return url_for('video_delete',
                channel=self.channel.name, playlist=self.playlist.name,
                video=self.url_name, _external=_external)
        elif action == 'add-speaker':
            return url_for('video_add_speaker',
                channel=channel.name, playlist=playlist.name,
                video=self.url_name, _external=_external)
        elif action == 'remove-speaker':
            return url_for('video_remove_speaker',
                channel=channel.name, playlist=playlist.name,
                video=self.url_name, _external=_external)
        elif action == 'action':
            return url_for('video_action',
                channel=channel.name, playlist=playlist.name,
                video=self.url_name, _external=_external)

    def embed_video_for(self, action='view'):
        if self.video_source == u'youtube':
            if action == 'edit':
                return Markup('<iframe src="http://www.youtube.com/embed/%s?wmode=transparent&showinfo=0&rel=0&autohide=1&autoplay=0" frameborder="0" allowfullscreen></iframe>' % self.video_sourceid)
            elif action == 'view':
                return Markup('<iframe src="http://www.youtube.com/embed/%s?wmode=transparent&showinfo=0&rel=0&autohide=1&autoplay=1" frameborder="0" allowfullscreen></iframe>' % self.video_sourceid)
        return u''

    def embed_slides_for(self, action=None):
        if self.slides_source == u'speakerdeck':
            html = '<iframe src="http://www.speakerdeck.com/embed/%s" frameborder="0" marginwidth="0" marginheight="0" scrolling="no"></iframe>' % self.slides_sourceid
            return Markup(html)
        elif self.slides_source == u'slideshare':
            html = '<iframe src="http://www.slideshare.net/slideshow/embed_code/%s" frameborder="0" marginwidth="0" marginheight="0" scrolling="no"></iframe>' % self.slides_sourceid
            return Markup(html)
        return u''
