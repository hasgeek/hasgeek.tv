from datetime import date

from flask import url_for
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.orderinglist import ordering_list
from werkzeug.utils import cached_property

from baseframe import __, cache
from coaster.utils import LabeledEnum
from flask_lastuser.sqlalchemy import ProfileBase

from . import (
    PLAYLIST_AUTO_TYPE,
    BaseMixin,
    BaseScopedNameMixin,
    Model,
    backref,
    db,
    relationship,
    sa,
    sa_orm,
)
from .video import PlaylistVideo, Video

__all__ = ['CHANNEL_TYPE', 'PLAYLIST_TYPE', 'Channel', 'Playlist', 'PlaylistRedirect']


class CHANNEL_TYPE(LabeledEnum):  # noqa: N801
    UNDEFINED = (0, __("Channel"))
    PERSON = (1, __("Person"))
    ORGANIZATION = (2, __("Organization"))
    EVENTSERIES = (3, __("Event Series"))


class PLAYLIST_TYPE(LabeledEnum):  # noqa: N801
    REGULAR = (0, __("Playlist"))
    EVENT = (1, __("Event"))


class Channel(ProfileBase, Model):
    __tablename__ = 'channel'
    description = sa_orm.mapped_column(sa.UnicodeText, default='', nullable=False)
    bio = sa_orm.mapped_column(sa.Unicode(250), nullable=True)
    featured = sa_orm.mapped_column(sa.Boolean, default=False, nullable=False)
    type = sa_orm.mapped_column(  # noqa: A003
        sa.Integer, default=CHANNEL_TYPE.UNDEFINED, nullable=False
    )
    channel_logo_filename = sa_orm.mapped_column(
        sa.Unicode(250), nullable=True, default=''
    )
    channel_banner_url = sa_orm.mapped_column(sa.Unicode(250), nullable=True)

    __roles__ = {
        'all': {'read': {'title', 'name', 'description', 'featured'}},
        'auth': {'read': {'current_action_permissions'}},
    }

    def __repr__(self):
        return f'<Channel {self.name} "{self.title}">'

    @property
    def current_action_permissions(self):
        """
        Returns all the valid action permissions provided by the model based on user
        role. This is needed for JSON endpoints when they return current_access(), and
        front-end has to know what actions the user can perform on the given model
        object.
        """
        return list(
            {'delete', 'new-video', 'edit', 'new-playlist'}.intersection(
                self.current_permissions
            )
        )

    def type_label(self):
        return CHANNEL_TYPE.get(self.type, CHANNEL_TYPE[0])

    @classmethod
    @cache.cached(key_prefix='data/featured-channels')
    def get_featured(cls):
        return (
            cls.query.join(Playlist)
            .join(Video)
            .filter(Channel.featured.is_(True))
            .order_by(Video.created_at.desc())
            .all()
        )

    @cached_property
    def user_playlists(self):
        """
        User-created (non-auto) playlists.
        """
        return [p for p in self.playlists if p.auto_type is None]

    @property
    def speaker_details(self):
        """
        For a speaker channel, this returns the speaker's pickername and
        the url to the playlist of all the videos of the speaker speaking
        """
        playlist_speaking = self.playlist_for_speaking_in()
        speaker_dict = {
            'pickername': self.pickername,
            # 'externalid': self.externalid if self.externalid else '',
            'playlist_for_speaking_in': (
                playlist_speaking.url_for('view') if playlist_speaking else ''
            ),
        }
        return speaker_dict

    def get_auto_playlist(self, auto_type, create=False, public=False):
        with db.session.no_autoflush:
            playlist = Playlist.query.filter_by(
                channel=self, auto_type=auto_type
            ).first()
        if playlist is None and create:
            playlist = Playlist(
                channel=self,
                auto_type=auto_type,
                name=PLAYLIST_AUTO_TYPE[auto_type].name,
                title=PLAYLIST_AUTO_TYPE[auto_type].title,
                public=public,
            )  # Automatic playlists are hidden by default
            db.session.add(playlist)
        return playlist

    def auto_playlists(self):
        """
        Returns a dictionary of playlist_code: playlist
        """
        return {
            playlist.auto_type: playlist
            for playlist in Playlist.query.filter_by(channel=self).filter(
                Playlist.auto_type is not None
            )
        }

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
        roles = super().roles_for(actor, anchors)
        if actor and self.userid in actor.user_organizations_owned_ids():
            roles.add('channel_admin')
        return roles

    def permissions(self, user, inherited=None):
        perms = super().permissions(user, inherited)
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


class Playlist(BaseScopedNameMixin, Model):
    __tablename__ = 'playlist'
    channel_id = sa_orm.mapped_column(
        sa.Integer, sa.ForeignKey('channel.id'), nullable=False
    )
    description = sa_orm.mapped_column(sa.UnicodeText, default='', nullable=False)
    public = sa_orm.mapped_column(sa.Boolean, nullable=False, default=True)
    recorded_date = sa_orm.mapped_column(sa.Date, nullable=True)
    published_date = sa_orm.mapped_column(sa.Date, nullable=False, default=date.today)
    featured = sa_orm.mapped_column(sa.Boolean, default=False, nullable=False)
    type = sa_orm.mapped_column(  # noqa: A003
        sa.Integer, default=PLAYLIST_TYPE.REGULAR, nullable=False
    )
    auto_type = sa_orm.mapped_column(sa.Integer, nullable=True)
    banner_ad_filename = sa_orm.mapped_column(
        sa.Unicode(250), nullable=True, default=''
    )
    banner_ad_url = sa_orm.mapped_column(sa.Unicode(250), nullable=True, default='')
    channel = relationship(
        Channel,
        primaryjoin=channel_id == Channel.id,
        backref=backref(
            'playlists',
            order_by=(recorded_date.desc(), published_date.desc()),
            cascade='all, delete-orphan',
        ),
    )
    parent = sa_orm.synonym('channel')

    __table_args__ = (
        sa.UniqueConstraint('channel_id', 'auto_type'),
        sa.UniqueConstraint('channel_id', 'name'),
    )

    _videos = relationship(
        PlaylistVideo,
        order_by=[PlaylistVideo.seq],
        collection_class=ordering_list('seq'),
        backref='playlist',
        cascade='all, delete-orphan',
    )
    videos = association_proxy(
        '_videos', 'video', creator=lambda x: PlaylistVideo(video=x)
    )

    __roles__ = {
        'all': {
            'read': {'title', 'name', 'description', 'featured'},
        },
        'auth': {'read': {'current_action_permissions'}},
    }

    def __repr__(self):
        if self.auto_type:
            return '<AutoPlaylist {} of {}>'.format(
                self.type_label(), self.channel.title
            )
        else:
            return f'<Playlist {self.title} of {self.channel.title}>'

    @property
    def current_action_permissions(self):
        """
        Returns all the valid action permissions provided by the model based on user
        role. This is needed for JSON endpoints when they return current_access(), and
        front-end has to know what actions the user can perform on the given model
        object.
        """
        return list(
            {
                'delete',
                'new-video',
                'edit',
                'extend',
                'add-video',
                'remove-video',
            }.intersection(self.current_permissions)
        )

    @property
    def featured_videos_list(self):
        """
        Returns current_access() along with the list of current_access() of the featured
        videos in the playlist
        """
        return [dict(video.current_access()) for video in self.videos[:4]]

    @property
    def videos_list(self):
        """
        Returns current_access() along with the list of current_access() of the all the
        videos in the playlist
        """
        return [dict(video.current_access()) for video in self.videos]

    # These two methods below work like current_access() but with different number of videos in them.
    # The videos are dictionaries instead of RoleAccessProxy as these are mostly used for front-end use now.
    # We're casting them to dict() here instead of in the view.
    # Depending on need, Use -
    #
    # current_access_with_all_videos() - if a playlist might need to return all videos in it (playlist page),
    # current_access_with_featured_videos() - only the features videos (home page),
    # current_access() - no videos just metadata (anywhere else where video list is unnecessary).
    #
    # Use these accordingly.
    # TODO: Remove these once current_access() supports relationships
    #
    def current_access_with_all_videos(self):
        playlist_dict = dict(self.current_access())
        playlist_dict['videos'] = self.videos_list
        return playlist_dict

    def current_access_with_featured_videos(self):
        playlist_dict = dict(self.current_access())
        playlist_dict['videos'] = self.featured_videos_list
        return playlist_dict

    @classmethod
    def get_featured(cls, count):
        return (
            cls.query.filter_by(public=True, auto_type=None, featured=True)
            .order_by(cls.featured.desc(), cls.updated_at)
            .limit(count)
            .all()
        )

    @classmethod
    def migrate_profile(cls, oldchannel, newchannel):
        """
        Move all playlists from the old channel to the new channel.
        """

        def move_playlist(playlist, channel):
            """
            Move playlist to a new channel
            """
            conflict = bool(
                playlist.query.filter_by(name=playlist.name, channel=channel).count()
            )
            playlist.channel = channel
            if conflict:
                playlist.make_name()

        for playlist in oldchannel.playlists:
            if playlist.auto_type:
                # Check for matching playlist in newchannel
                newplaylist = newchannel.get_auto_playlist(
                    auto_type=playlist.auto_type, create=False
                )
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

    def roles_for(self, actor=None, anchors=()):
        roles = super().roles_for(actor, anchors)
        roles.update(self.channel.roles_for(actor, anchors))
        if 'channel_admin' in roles:
            roles.add('playlist_admin')
        return roles

    def permissions(self, user, inherited=None):
        perms = super().permissions(user, inherited)
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
            return url_for(
                'playlist_view',
                channel=self.channel.name,
                playlist=self.name,
                _external=_external,
            )
        elif action == 'feed':
            return url_for(
                'playlist_feed',
                channel=self.channel.name,
                playlist=self.name,
                _external=_external,
            )
        elif action == 'edit':
            return url_for(
                'playlist_edit',
                channel=self.channel.name,
                playlist=self.name,
                _external=_external,
            )
        elif action == 'extend':
            return url_for(
                'playlist_extend',
                channel=self.channel.name,
                playlist=self.name,
                _external=_external,
            )
        elif action == 'delete':
            return url_for(
                'playlist_delete',
                channel=self.channel.name,
                playlist=self.name,
                _external=_external,
            )
        elif action == 'new-video':
            return url_for(
                'video_new',
                channel=self.channel.name,
                playlist=self.name,
                _external=_external,
            )

    def next(self, video):  # noqa: A003
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


class PlaylistRedirect(BaseMixin, Model):
    __tablename__ = "playlist_redirect"

    channel_id = sa_orm.mapped_column(None, sa.ForeignKey('channel.id'), nullable=False)
    channel = relationship(
        Channel, backref=backref('playlist_redirects', cascade='all, delete-orphan')
    )

    name = sa_orm.mapped_column(sa.Unicode(250), nullable=False)
    playlist_id = sa_orm.mapped_column(
        None, sa.ForeignKey('playlist.id'), nullable=False
    )
    playlist = relationship(
        Playlist, backref=backref('redirects', cascade='all, delete-orphan')
    )

    __table_args__ = (sa.UniqueConstraint(channel_id, name),)

    def redirect_view_args(self):
        return {'playlist': self.playlist.name}

    @classmethod
    def migrate_profile(cls, oldchannel, newchannel):
        """
        There's no point trying to migrate playlists when merging channels, so discard them.
        """
        oldchannel.playlist_redirects = []
        return [cls.__table__.name]
