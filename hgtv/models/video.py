# -*- coding: utf-8 -*-

import urllib
from sqlalchemy.ext.associationproxy import association_proxy
from werkzeug import cached_property
from flask import Markup, url_for, current_app, g
from flask_commentease import CommentingMixin
from hgtv.models import db, TimestampMixin, BaseIdNameMixin, PLAYLIST_AUTO_TYPE
from hgtv.models.tag import tags_videos

__all__ = ['PlaylistVideo', 'Video']


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
    thumbnail_path = db.Column(db.Unicode(250), nullable=True, default=u'')

    video_source = db.Column(db.Unicode(80), nullable=False, default=u'')
    video_sourceid = db.Column(db.Unicode(80), nullable=False, default=u'')

    slides_source = db.Column(db.Unicode(80), nullable=False, default=u'')
    slides_sourceid = db.Column(db.Unicode(80), nullable=False, default=u'')
    video_slides_mapping = db.Column(db.UnicodeText, nullable=True, default=u'')
    video_slides_mapping_json = db.Column(db.UnicodeText, nullable=True, default=u'')

    playlists = association_proxy('_playlists', 'playlist', creator=lambda x: PlaylistVideo(playlist=x))

    tags = db.relationship('Tag', secondary=tags_videos, backref=db.backref('videos'))

    __roles__ = {
        'viewer': {
            'read': {'title', 'name', 'description', 'url', 'url_name', 'thumbnail'},
            },
        }

    def __repr__(self):
        return u'<Video %s>' % self.url_name

    @property
    def url(self):
        return self.url_for(_external=True)

    @property
    def thumbnail(self):
        return url_for('static', filename='thumbnails/' + self.thumbnail_path)

    @cached_property
    def speakers(self):
        return [plv.playlist.channel for plv in PlaylistVideo.query.filter_by(video=self) if plv.playlist.auto_type == PLAYLIST_AUTO_TYPE.SPEAKING_IN]

    def get_details(self, playlist):
        video_dict = dict(self.current_access())
        video_dict['speakers'] = [speaker.pickername for speaker in self.speakers]
        video_dict['not_part_playlist'] = {'name': self.playlist.name, 'title': self.playlist.title} if playlist != self.playlist else False
        return video_dict

    def get_embed_details(self, playlist):
        video_dict = self.get_details(playlist)
        video_dict.update({
            'video_iframe': self.embed_video_for(current_app.config.get('VIDEO_VIEW_MODE', 'view')),
            'video_source': self.video_source,
            'slides_html': self.embed_slides_for('view'),
            'slides_source': self.slides_source
            })
        return video_dict

    def get_action_permissions(self, playlist):
        video_dict = {
            'action_url': self.url_for('action') if g.user else '',
            'remove_permission': 'remove-video' in playlist.permissions(g.user) and playlist != self.playlist,
            'edit_permission': 'edit' in self.permissions(g.user),
            'delete_permission': 'delete' in self.permissions(g.user),
            'user_playlists_url': url_for('user_playlists', video=self.url_name) if 'edit' in g.permissions else False
        }
        return video_dict

    def get_related_videos(self, playlist):
        videos_dict = []
        if playlist.next(video=self):
            videos_dict.append(playlist.next(video=self).get_details(playlist))
        if playlist.prev(video=self):
            videos_dict.append(playlist.prev(video=self).get_details(playlist))
        return videos_dict

    def permissions(self, user, inherited=None):
        perms = super(Video, self).permissions(user, inherited)
        perms.add('view')
        if user and self.channel.userid in user.user_organizations_owned_ids():
            perms.add('edit')
            perms.add('delete')
        else:
            perms.discard('edit')
            perms.discard('delete')
        # Allow speakers to edit
        if user:
            pl = user.channel.playlist_for_speaking_in()
            if pl and self in pl.videos:
                perms.add('edit')
        return perms

    def roles_for(self, actor=None, anchors=()):
        # Calling super give us a result set with the standard roles
        result = super(Video, self).roles_for(actor, anchors)
        result.add('viewer')
        return result

    def url_for(self, action='view', channel=None, playlist=None, _external=False):
        channel = channel or self.channel
        playlist = playlist or self.playlist
        if playlist.channel != channel or playlist not in self.playlists:
            return
        if action == 'view':
            return url_for('video_view',
                videopath='%s/%s/%s' % (channel.name, playlist.name, self.url_name),
                _external=_external)
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
        elif action == 'autocomplete-speaker':
            return url_for('video_autocomplete_speaker',
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
                return Markup('<iframe id="youtube_player" src="//www.youtube.com/embed/%s?wmode=transparent&showinfo=0&rel=0&autohide=0&autoplay=0&enablejsapi=1&version=3" frameborder="0" allowfullscreen></iframe>' % self.video_sourceid)
            elif action == 'view':
                return Markup('<iframe id="youtube_player" src="//videoken.com/embed/?videoID=%s&wmode=transparent&showinfo=0&rel=0&autohide=0&autoplay=1&enablejsapi=1&version=3" frameborder="0" allowfullscreen></iframe>' % self.video_sourceid)
        elif self.video_source == u"vimeo":
            if action == 'edit':
                return Markup('<iframe id="vimeo_player" src="//player.vimeo.com/video/%s?api=1&player_id=vimeoplayer" frameborder="0" webkitAllowFullScreen mozallowfullscreen allowFullScreen></iframe>' % self.video_sourceid)
            elif action == 'view':
                return Markup('<iframe id="vimeo_player" src="//player.vimeo.com/video/%s?api=1&autoplay=1" frameborder="0" webkitAllowFullScreen mozallowfullscreen allowFullScreen></iframe>' % self.video_sourceid)
        elif self.video_source == u"ustream":
            if action == 'edit':
                return Markup('<iframe id="ustream_player" src="//www.ustream.tv/embed/%s?v=3&amp;wmode=direct" scrolling="no" frameborder="0" style="border: 0px none transparent;"> </iframe>' % self.video_sourceid)
            elif action == 'view':
                return Markup('<iframe id="ustream_player" src="//www.ustream.tv/embed/%s?v=3&amp;wmode=direct" scrolling="no" frameborder="0" style="border: 0px none transparent;"> </iframe>' % self.video_sourceid)
        return u''

    def embed_slides_for(self, action=None):
        if self.slides_source == u'speakerdeck':
            html = '<iframe src="//www.speakerdeck.com/embed/%s" frameborder="0" marginwidth="0" marginheight="0" scrolling="no"></iframe>' % urllib.quote(self.slides_sourceid)
            return Markup(html)
        elif self.slides_source == u'slideshare':
            html = '<iframe id="slideshare" src="//www.slideshare.net/slideshow/embed_code/%s" frameborder="0" marginwidth="0" marginheight="0" scrolling="no"></iframe>' % urllib.quote(self.slides_sourceid)
            return Markup(html)
        return u''
