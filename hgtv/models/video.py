import urllib.error
import urllib.parse

from flask import current_app, url_for
from markupsafe import Markup
from sqlalchemy.ext.associationproxy import association_proxy
from werkzeug.utils import cached_property

from ..models import PLAYLIST_AUTO_TYPE, BaseIdNameMixin, TimestampMixin, db
from .tag import tags_videos

__all__ = ['PlaylistVideo', 'Video']


class PlaylistVideo(TimestampMixin, db.Model):
    __tablename__ = 'playlist_video'
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.id'), primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), primary_key=True)
    video = db.relationship(
        'Video', backref=db.backref('_playlists', cascade='all, delete-orphan')
    )
    seq = db.Column(db.Integer, nullable=False)
    description = db.Column(db.UnicodeText, nullable=False, default=True)


class Video(BaseIdNameMixin, db.Model):
    __tablename__ = 'video'
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.id'), nullable=False)
    playlist = db.relationship(
        'Playlist', backref=db.backref('primary_videos', cascade='all, delete-orphan')
    )
    channel = association_proxy('playlist', 'channel')
    description = db.Column(db.UnicodeText, nullable=False, default='')
    video_url = db.Column(db.Unicode(250), nullable=False)
    slides_url = db.Column(db.Unicode(250), nullable=False, default='')
    thumbnail_path = db.Column(db.Unicode(250), nullable=True, default='')

    video_source = db.Column(db.Unicode(80), nullable=False, default='')
    video_sourceid = db.Column(db.Unicode(80), nullable=False, default='')

    slides_source = db.Column(db.Unicode(80), nullable=False, default='')
    slides_sourceid = db.Column(db.Unicode(80), nullable=False, default='')
    video_slides_mapping = db.Column(db.UnicodeText, nullable=True, default='')
    video_slides_mapping_json = db.Column(db.UnicodeText, nullable=True, default='')

    playlists = association_proxy(
        '_playlists', 'playlist', creator=lambda x: PlaylistVideo(playlist=x)
    )

    tags = db.relationship('Tag', secondary=tags_videos, backref=db.backref('videos'))

    __roles__ = {
        'all': {
            'read': {
                'title',
                'name',
                'description',
                'url',
                'url_name',
                'thumbnail',
                'speaker_names',
                'video_source',
                'slides_source',
                'video_iframe',
                'slides_html',
            },
        },
        'auth': {'read': {'url_action', 'current_action_permissions'}},
        'channel_admin': {'read': {'url_user_playlists', 'url_action'}},
        'speaker': {'read': {'url_user_playlists', 'url_action'}},
    }

    def __repr__(self):
        return '<Video %s>' % self.url_name

    # ====================
    # RoleMixin properties
    # ====================
    @property
    def url(self):
        """
        URL to this video. For use with RoleMixin, in ``__roles__``.
        """
        return self.url_for(_external=True)

    @property
    def url_action(self):
        return self.url_for('action')

    @property
    def url_user_playlists(self):
        return url_for('user_playlists', video=self.url_name)

    @property
    def thumbnail(self):
        return url_for('static', filename='thumbnails/' + self.thumbnail_path)

    @property
    def speaker_names(self):
        """
        For use with RoleMixin above, in ``__roles__``.
        """
        return [speaker.pickername for speaker in self.speakers]

    @property
    def current_action_permissions(self):
        """
        Returns all the valid action permissions provided by the model based on user role.
        This is needed for JSON endpoints when they return current_access(), and front-end has to
        know what actions the user can perform on the givem model object.
        """
        return list({'delete', 'edit'}.intersection(self.current_permissions))

    @property
    def video_iframe(self):
        return self.embed_video_for(current_app.config.get('VIDEO_VIEW_MODE', 'view'))

    @property
    def slides_html(self):
        return self.embed_slides_for()

    @cached_property
    def speakers(self):
        from .channel import Playlist

        return [
            plv.playlist.channel
            for plv in PlaylistVideo.query.join(Playlist).filter(
                PlaylistVideo.video == self,
                Playlist.auto_type == PLAYLIST_AUTO_TYPE.SPEAKING_IN,
            )
        ]

    def get_related_videos(self, playlist):
        videos_dict = []
        next_video = playlist.next(video=self)
        if next_video:
            videos_dict.append(dict(next_video.current_access()))
        prev_video = playlist.prev(video=self)
        if prev_video:
            videos_dict.append(dict(prev_video.current_access()))
        return videos_dict

    def permissions(self, user, inherited=None):
        perms = super().permissions(user, inherited)
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
        roles = super().roles_for(actor, anchors)
        roles.update(self.playlist.roles_for(actor, anchors))
        if actor is not None:
            # whether user is speaker
            pl = actor.channel.playlist_for_speaking_in()
            if pl and self in pl.videos:
                roles.add('speaker')
        return roles

    def url_for(self, action='view', channel=None, playlist=None, _external=False):
        channel = channel or self.channel
        playlist = playlist or self.playlist
        if playlist.channel != channel or playlist not in self.playlists:
            return
        if action == 'view':
            return url_for(
                'video_view',
                videopath=f'{channel.name}/{playlist.name}/{self.url_name}',
                _external=_external,
            )
        elif action == 'remove-video':
            return url_for(
                'video_remove',
                channel=channel.name,
                playlist=playlist.name,
                video=self.url_name,
                _external=_external,
            )
        # Edit and Delete can only be from the source playlist
        elif action == 'edit':
            return url_for(
                'video_edit',
                channel=self.channel.name,
                playlist=self.playlist.name,
                video=self.url_name,
                _external=_external,
            )
        elif action == 'delete':
            return url_for(
                'video_delete',
                channel=self.channel.name,
                playlist=self.playlist.name,
                video=self.url_name,
                _external=_external,
            )
        elif action == 'add-speaker':
            return url_for(
                'video_add_speaker',
                channel=channel.name,
                playlist=playlist.name,
                video=self.url_name,
                _external=_external,
            )
        elif action == 'autocomplete-speaker':
            return url_for(
                'video_autocomplete_speaker',
                channel=channel.name,
                playlist=playlist.name,
                video=self.url_name,
                _external=_external,
            )
        elif action == 'remove-speaker':
            return url_for(
                'video_remove_speaker',
                channel=channel.name,
                playlist=playlist.name,
                video=self.url_name,
                _external=_external,
            )
        elif action == 'action':
            return url_for(
                'video_action',
                channel=channel.name,
                playlist=playlist.name,
                video=self.url_name,
                _external=_external,
            )

    def embed_video_for(self, action='view'):
        if self.video_source == 'youtube':
            if action == 'edit':
                return Markup(
                    '<iframe id="youtube_player" src="//www.youtube.com/embed/%s?wmode=transparent&showinfo=0&rel=0&autohide=0&autoplay=0&enablejsapi=1&version=3" frameborder="0" allowfullscreen></iframe>'
                    % self.video_sourceid
                )
            elif action == 'view':
                return Markup(
                    '<iframe id="youtube_player" src="//videoken.com/embed/?videoID=%s&wmode=transparent&showinfo=0&rel=0&autohide=0&autoplay=1&enablejsapi=1&version=3" frameborder="0" allowfullscreen></iframe>'
                    % self.video_sourceid
                )
        elif self.video_source == "vimeo":
            if action == 'edit':
                return Markup(
                    '<iframe id="vimeo_player" src="//player.vimeo.com/video/%s?api=1&player_id=vimeoplayer" frameborder="0" webkitAllowFullScreen mozallowfullscreen allowFullScreen></iframe>'
                    % self.video_sourceid
                )
            elif action == 'view':
                return Markup(
                    '<iframe id="vimeo_player" src="//player.vimeo.com/video/%s?api=1&autoplay=1" frameborder="0" webkitAllowFullScreen mozallowfullscreen allowFullScreen></iframe>'
                    % self.video_sourceid
                )
        elif self.video_source == "ustream":
            if action == 'edit':
                return Markup(
                    '<iframe id="ustream_player" src="//www.ustream.tv/embed/%s?v=3&amp;wmode=direct" scrolling="no" frameborder="0" style="border: 0px none transparent;"> </iframe>'
                    % self.video_sourceid
                )
            elif action == 'view':
                return Markup(
                    '<iframe id="ustream_player" src="//www.ustream.tv/embed/%s?v=3&amp;wmode=direct" scrolling="no" frameborder="0" style="border: 0px none transparent;"> </iframe>'
                    % self.video_sourceid
                )
        return ''

    def embed_slides_for(self, action=None):
        if self.slides_source == 'speakerdeck':
            html = (
                '<iframe src="//www.speakerdeck.com/embed/%s" frameborder="0" marginwidth="0" marginheight="0" scrolling="no"></iframe>'
                % urllib.parse.quote(self.slides_sourceid)
            )
            return Markup(html)
        elif self.slides_source == 'slideshare':
            html = (
                '<iframe id="slideshare" src="//www.slideshare.net/slideshow/embed_code/%s" frameborder="0" marginwidth="0" marginheight="0" scrolling="no"></iframe>'
                % urllib.parse.quote(self.slides_sourceid)
            )
            return Markup(html)
        return ''
