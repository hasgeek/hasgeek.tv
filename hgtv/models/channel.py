# -*- coding: utf-8 -*-

from datetime import date

from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.ext.associationproxy import association_proxy

from werkzeug import cached_property
from flask import url_for

from hgtv.models import db, BaseNameMixin, BaseScopedNameMixin, PLAYLIST_AUTO_TYPE, playlist_auto_types
from hgtv.models.video import ChannelVideo, PlaylistVideo


__all__ = ['CHANNEL_TYPE', 'PLAYLIST_TYPE', 'Channel', 'Playlist']


class CHANNEL_TYPE:
    UNDEFINED = 0
    PERSON = 1
    ORGANIZATION = 2
    EVENTSERIES = 3


class PLAYLIST_TYPE:
    REGULAR = 0
    EVENT = 1


channel_types = {
    0: u"Channel",
    1: u"Person",
    2: u"Organization",
    3: u"Event Series",
    }

playlist_types = {
    0: u"Playlist",
    1: u"Event",
    }


class Channel(BaseNameMixin, db.Model):
    __tablename__ = 'channel'
    userid = db.Column(db.Unicode(22), nullable=False, unique=True)
    description = db.Column(db.UnicodeText, default=u'', nullable=False)
    featured = db.Column(db.Boolean, default=False, nullable=False)
    type = db.Column(db.Integer, default=CHANNEL_TYPE.UNDEFINED, nullable=False)

    _videos = db.relationship(ChannelVideo,
        order_by=[ChannelVideo.seq],
        collection_class=ordering_list('seq'),
        backref='channel',
        cascade='all, delete-orphan')
    videos = association_proxy('_videos', 'video', creator=lambda x: ChannelVideo(video=x))

    def type_label(self):
        return channel_types.get(self.type, channel_types[0])

    @classmethod
    def get_featured(cls):
        return cls.query.filter_by(featured=True).order_by('featured').order_by(Channel.name.asc()).all()

    @cached_property
    def user_playlists(self):
        """
        User-created (non-auto) playlists.
        """
        return [p for p in self.playlists if p.auto_type is None]

    def get_auto_playlist(self, auto_type, create=False, public=False):
        playlist = Playlist.query.filter_by(channel=self, auto_type=auto_type).first()
        if playlist is None and create:
            playlist = Playlist(channel=self,
                auto_type=auto_type,
                title=playlist_auto_types.get(auto_type),
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
    short_title = db.Column(db.Unicode(80), nullable=False, default=u'')
    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'), nullable=False)
    description = db.Column(db.UnicodeText, default=u'', nullable=False)
    public = db.Column(db.Boolean, nullable=False, default=True)
    recorded_date = db.Column(db.Date, nullable=True)
    published_date = db.Column(db.Date, nullable=False, default=date.today)
    featured = db.Column(db.Boolean, default=False, nullable=False)
    type = db.Column(db.Integer, default=PLAYLIST_TYPE.REGULAR, nullable=False)
    auto_type = db.Column(db.Integer, nullable=True)
    channel = db.relationship(Channel, primaryjoin=channel_id == Channel.id,
        backref=db.backref('playlists', order_by=(recorded_date.desc(), published_date.desc()),
            cascade='all, delete-orphan'))
    parent = db.synonym('channel')

    __table_args__ = (db.UniqueConstraint('channel_id', 'auto_type'),
                      db.UniqueConstraint('channel_id', 'name'))

    _videos = db.relationship(PlaylistVideo,
        order_by=[PlaylistVideo.seq],
        collection_class=ordering_list('seq'),
        backref='playlist',
        cascade='all, delete-orphan')
    videos = association_proxy('_videos', 'video', creator=lambda x: PlaylistVideo(video=x))

    def __repr__(self):
        if self.auto_type:
            return '<AutoPlaylist %s of %s>' % (self.type_label(), self.channel.title)
        else:
            return '<Playlist %s of %s>' % (self.title, self.channel.title)

    @classmethod
    def get_featured(cls, count):
        return cls.query.filter_by(public=True, auto_type=None, featured=True).order_by('featured').order_by('updated_at').limit(count).all()

    def type_label(self):
        if self.auto_type is not None:
            return playlist_auto_types.get(self.auto_type)
        else:
            return playlist_types.get(self.type, playlist_types[0])

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
