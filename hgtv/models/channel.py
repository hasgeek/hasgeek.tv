# -*- coding: utf-8 -*-

from datetime import date

from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.ext.associationproxy import association_proxy
from coaster.utils import LabeledEnum
from baseframe import cache

from werkzeug import cached_property
from flask_lastuser.sqlalchemy import ProfileBase
from flask import url_for, g

from .video import PlaylistVideo, Video
from ..models import db, BaseMixin, BaseScopedNameMixin, PLAYLIST_AUTO_TYPE


__all__ = ['CHANNEL_TYPE', 'PLAYLIST_TYPE', 'Channel', 'Playlist', 'PlaylistRedirect']


class CHANNEL_TYPE(LabeledEnum):
    UNDEFINED = (0, u"Channel")
    PERSON = (1, u"Person")
    ORGANIZATION = (2, u"Organization")
    EVENTSERIES = (3, u"Event Series")


class PLAYLIST_TYPE(LabeledEnum):
    REGULAR = (0, u"Playlist")
    EVENT = (1, u"Event")


class Channel(ProfileBase, db.Model):
    __tablename__ = 'channel'
    description = db.Column(db.UnicodeText, default=u'', nullable=False)
    bio = db.Column(db.Unicode(250), nullable=True)
    featured = db.Column(db.Boolean, default=False, nullable=False)
    type = db.Column(db.Integer, default=CHANNEL_TYPE.UNDEFINED, nullable=False)
    channel_logo_filename = db.Column(db.Unicode(250), nullable=True, default=u'')
    channel_banner_url = db.Column(db.Unicode(250), nullable=True)

    __roles__ = {
        'all': {
            'read': {'title', 'name', 'description', 'featured', 'current_action_permissions'},
            },
        }

    def __repr__(self):
        return '<Channel %s "%s">' % (self.name, self.title)

    @property
    def current_action_permissions(self):
        return list({'delete', 'new-video', 'edit', 'new-playlsit'}.intersection(self.current_permissions))

    def type_label(self):
        return CHANNEL_TYPE.get(self.type, CHANNEL_TYPE[0])

    @classmethod
    @cache.cached(key_prefix='data/featured-channels')
    def get_featured(cls):
        return cls.query.join(Playlist).join(Video).filter(Channel.featured == True).order_by(Video.created_at.desc()).all()

    @cached_property
    def user_playlists(self):
        """
        User-created (non-auto) playlists.
        """
        return [p for p in self.playlists if p.auto_type is None]

    @property
    def speaker_details(self):
        playlist_speaking = self.playlist_for_speaking_in()
        speaker_dict = {
            'pickername': self.pickername,
            # 'externalid': self.externalid if self.externalid else '',
            'playlist_for_speaking_in': playlist_speaking.url_for('view') if playlist_speaking else ''
        }
        return speaker_dict

    def get_auto_playlist(self, auto_type, create=False, public=False):
        with db.session.no_autoflush:
            playlist = Playlist.query.filter_by(channel=self, auto_type=auto_type).first()
        if playlist is None and create:
            playlist = Playlist(channel=self,
                auto_type=auto_type,
                name=unicode(PLAYLIST_AUTO_TYPE[auto_type].name),
                title=unicode(PLAYLIST_AUTO_TYPE[auto_type].title),
                public=public)  # Automatic playlists are hidden by default
            db.session.add(playlist)
        return playlist

    def auto_playlists(self):
        """
        Returns a dictionary of playlist_code: playlist
        """
        return dict((playlist.auto_type, playlist) for playlist in Playlist.query.filter_by(
            channel=self).filter(Playlist.auto_type is not None))

    def playlist_for_watched(self, create=False):
        return self.get_auto_playlist(PLAYLIST_AUTO_TYPE.WATCHED, create, False)

    def playlist_for_liked(self, create=False):
        return self.get_auto_playlist(PLAYLIST_AUTO_TYPE.LIKED, create, False)

    def playlist_for_disliked(self, create=False):
        return self.get_auto_playlist(PLAYLIST_AUTO_TYPE.DISLIKED, create, False)

    def playlist_for_speaking_in(self, create=False):
        return self.get_auto_playlist(PLAYLIST_AUTO_TYPE.SPEAKING_IN, create, True)

    def playlist_for_appearing_in(self, create=False):
        return self.get_auto_playlist(PLAYLIST_AUTO_TYPE.APPEARING_IN, create, True)

    def playlist_for_crew_in(self, create=False):
        return self.get_auto_playlist(PLAYLIST_AUTO_TYPE.CREW_IN, create, True)

    def playlist_for_starred(self, create=False):
        return self.get_auto_playlist(PLAYLIST_AUTO_TYPE.STARRED, create, False)

    def playlist_for_queue(self, create=False):
        return self.get_auto_playlist(PLAYLIST_AUTO_TYPE.QUEUE, create, False)

    def playlist_for_stream(self, create=False):
        return self.get_auto_playlist(PLAYLIST_AUTO_TYPE.STREAM, create, True)

    def roles_for(self, actor=None, anchors=()):
        roles = super(Channel, self).roles_for(actor, anchors)
        if actor and self.userid in actor.user_organizations_owned_ids():
            roles.add('channel_admin')
        return roles

    def permissions(self, user, inherited=None):
        perms = super(Channel, self).permissions(user, inherited)
        perms.add('view')
        if user and self.userid in user.user_organizations_owned_ids():
            perms.add('edit')
            perms.add('delete')
            perms.add('new-playlist')
            perms.add('new-video')
        return perms

    def url_for(self, action='view', _external=False):
        if action == 'view':
            return url_for('channel_view', channel=self.name, _external=_external)
        elif action == 'feed':
            stream = self.playlist_for_stream(self, create=False)
            if stream is not None:
                return stream.url_for('feed')
        elif action == 'edit':
            return url_for('channel_edit', channel=self.name, _external=_external)
        elif action == 'new-playlist':
            return url_for('playlist_new', channel=self.name, _external=_external)
        elif action == 'import-playlist':
            return url_for('playlist_import', channel=self.name, _external=_external)
        elif action == 'action':
            return url_for('channel_action', channel=self.name, _external=_external)
        elif action == 'stream-add':
            return url_for('stream_new_video', channel=self.name, _external=_external)


class Playlist(BaseScopedNameMixin, db.Model):
    __tablename__ = 'playlist'
    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'), nullable=False)
    description = db.Column(db.UnicodeText, default=u'', nullable=False)
    public = db.Column(db.Boolean, nullable=False, default=True)
    recorded_date = db.Column(db.Date, nullable=True)
    published_date = db.Column(db.Date, nullable=False, default=date.today)
    featured = db.Column(db.Boolean, default=False, nullable=False)
    type = db.Column(db.Integer, default=PLAYLIST_TYPE.REGULAR, nullable=False)
    auto_type = db.Column(db.Integer, nullable=True)
    banner_ad_filename = db.Column(db.Unicode(250), nullable=True, default=u'')
    banner_ad_url = db.Column(db.Unicode(250), nullable=False, default=u'')
    channel = db.relationship(Channel, primaryjoin=channel_id == Channel.id,
        backref=db.backref('playlists', order_by=(recorded_date.desc(), published_date.desc()),
            cascade='all, delete-orphan'))
    parent = db.synonym('channel')

    __table_args__ = (db.UniqueConstraint('channel_id', 'auto_type'),
                      db.UniqueConstraint('channel_id', 'name'))

    _videos = db.relationship(PlaylistVideo, order_by=[PlaylistVideo.seq], collection_class=ordering_list('seq'),
        backref='playlist', cascade='all, delete-orphan')
    videos = association_proxy('_videos', 'video', creator=lambda x: PlaylistVideo(video=x))

    __roles__ = {
        'all': {
            'read': {'title', 'name', 'description', 'featured', 'current_action_permissions'},
            },
        }

    def __repr__(self):
        if self.auto_type:
            return '<AutoPlaylist %s of %s>' % (self.type_label(), self.channel.title)
        else:
            return '<Playlist %s of %s>' % (self.title, self.channel.title)

    @property
    def current_action_permissions(self):
        return list({'delete', 'new-video', 'edit', 'extend', 'add-video', 'remove-video'}.intersection(self.current_permissions))

    @property
    def featured_videos(self):
        return [video.get_details(playlist=self) for video in self.videos[:4]]

    @classmethod
    def get_featured(cls, count):
        return cls.query.filter_by(public=True, auto_type=None, featured=True
            ).order_by('featured').order_by('updated_at').limit(count).all()

    @classmethod
    def migrate_profile(cls, oldchannel, newchannel):
        """
        Move all playlists from the old channel to the new channel.
        """
        def move_playlist(playlist, channel):
            """
            Move playlist to a new channel
            """
            conflict = bool(playlist.query.filter_by(name=playlist.name, channel=channel).count())
            playlist.channel = channel
            if conflict:
                playlist.make_name()
        for playlist in oldchannel.playlists:
            if playlist.auto_type:
                # Check for matching playlist in newchannel
                newplaylist = newchannel.get_auto_playlist(auto_type=playlist.auto_type, create=False)
                if not newplaylist:
                    move_playlist(playlist, newchannel)
                else:
                    while playlist._videos:
                        plv = playlist._videos.pop(0)
                        if plv.video not in newplaylist.videos:
                            newplaylist._videos.append(plv)
                    for video in playlist.primary_videos:
                        video.playlist = newplaylist
                    db.session.delete(playlist)
            else:
                move_playlist(playlist, newchannel)
        return [cls.__table__.name, PlaylistVideo.__table__.name]

    def type_label(self):
        if self.auto_type is not None:
            return PLAYLIST_AUTO_TYPE[self.auto_type].title
        else:
            return PLAYLIST_TYPE.get(self.type, PLAYLIST_TYPE[0])

    def get_details(self, video_type='all'):
        playlist_dict = dict(self.current_access())
        if self.videos and video_type != 'none':
            if video_type == 'featured':
                videos = self.videos[:4]
            else:
                videos = self.videos
            playlist_dict['videos'] = [video.get_details(playlist=self) for video in videos]
        return playlist_dict

    def get_action_permissions(self):
        return {
            'delete_permission': 'delete' in self.permissions(g.user),
            'add_video_permission': 'new-video' in self.permissions(g.user),
            'edit_permission': 'edit' in self.permissions(g.user),
            'extend_permission': 'extend' in self.permissions(g.user)
        }

    def roles_for(self, actor=None, anchors=()):
        roles = super(Playlist, self).roles_for(actor, anchors)
        roles.update(self.channel.roles_for(actor, anchors))
        if 'channel_admin' in roles:
            roles.add('playlist_admin')
        return roles

    def permissions(self, user, inherited=None):
        perms = super(Playlist, self).permissions(user, inherited)
        if self.public:
            perms.add('view')
        if user and self.channel.userid in user.user_organizations_owned_ids():
            perms.add('view')  # In case playlist is not public
            perms.add('edit')
            perms.add('delete')
            if not self.auto_type or self.auto_type == PLAYLIST_AUTO_TYPE.STREAM:
                perms.add('new-video')
                perms.add('extend')
            perms.add('add-video')
            perms.add('remove-video')
        return perms

    def url_for(self, action='view', _external=False):
        if action == 'view':
            return url_for('playlist_view', channel=self.channel.name, playlist=self.name, _external=_external)
        elif action == 'feed':
            return url_for('playlist_feed', channel=self.channel.name, playlist=self.name, _external=_external)
        elif action == 'edit':
            return url_for('playlist_edit', channel=self.channel.name, playlist=self.name, _external=_external)
        elif action == 'extend':
            return url_for('playlist_extend', channel=self.channel.name, playlist=self.name, _external=_external)
        elif action == 'delete':
            return url_for('playlist_delete', channel=self.channel.name, playlist=self.name, _external=_external)
        elif action == 'new-video':
            return url_for('video_new', channel=self.channel.name, playlist=self.name, _external=_external)

    def next(self, video):
        for index, _video in enumerate(self.videos):
            if video is _video:
                try:
                    return self.videos[index + 1]
                except IndexError:
                    return None
        else:
            return None

    def prev(self, video):
        for index, _video in enumerate(self.videos):
            if video is _video:
                if index == 0:
                    return None
                try:
                    return self.videos[index - 1]
                except IndexError:
                    return None
        else:
            return None


class PlaylistRedirect(BaseMixin, db.Model):
    __tablename__ = "playlist_redirect"

    channel_id = db.Column(None, db.ForeignKey('channel.id'), nullable=False)
    channel = db.relationship(Channel, backref=db.backref('playlist_redirects', cascade='all, delete-orphan'))

    name = db.Column(db.Unicode(250), nullable=False)
    playlist_id = db.Column(None, db.ForeignKey('playlist.id'), nullable=False)
    playlist = db.relationship(Playlist, backref=db.backref('redirects', cascade='all, delete-orphan'))

    __table_args__ = (db.UniqueConstraint(channel_id, name),)

    def redirect_view_args(self):
        return {'playlist': self.playlist.name}

    @classmethod
    def migrate_profile(cls, oldchannel, newchannel):
        """
        There's no point trying to migrate playlists when merging channels, so discard them.
        """
        oldchannel.playlist_redirects = []
        return [cls.__table__.name]
