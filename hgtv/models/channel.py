# -*- coding: utf-8 -*-

from datetime import date

from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.ext.associationproxy import association_proxy

from flask import url_for

from hgtv.models import db, BaseNameMixin
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


class PLAYLIST_AUTO_TYPE:
    WATCHED = 1
    ATTENDED = 2
    LIKED = 3
    DISLIKED = 4
    SPEAKING_IN = 5
    APPEARING_IN = 6
    CREW_IN = 7


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

playlist_auto_types = {
    1: u"Watched",
    2: u"Attended",
    3: u"Liked",
    4: u"Disliked",
    5: u"Speaking in",
    6: u"Appearing in",
    7: u"Crew in",
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

    def permissions(self, user, inherited=None):
        perms = super(Channel, self).permissions(user, inherited)
        perms.add('view')
        if user and self.userid in user.user_organizations_owned_ids():
            perms.add('edit')
            perms.add('delete')
            perms.add('new-playlist')
        return perms

    def url_for(self, action='view'):
        if action == 'view':
            return url_for('channel_view', channel=self.name)
        elif action == 'edit':
            return url_for('channel_edit', channel=self.name)
        elif action == 'new-playlist':
            return url_for('playlist_new', channel=self.name)


class Playlist(BaseNameMixin, db.Model):
    __tablename__ = 'playlist'
    short_title = db.Column(db.Unicode(80), nullable=False, default=u'')
    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'), nullable=False)
    channel = db.relationship(Channel, primaryjoin=channel_id == Channel.id,
        backref=db.backref('playlists', cascade='all, delete-orphan'))
    description = db.Column(db.UnicodeText, default=u'', nullable=False)
    public = db.Column(db.Boolean, nullable=False, default=True)
    recorded_date = db.Column(db.Date, nullable=True)
    published_date = db.Column(db.Date, nullable=False, default=date.today)
    featured = db.Column(db.Boolean, default=False, nullable=False)
    type = db.Column(db.Integer, default=PLAYLIST_TYPE.REGULAR, nullable=False)
    auto_type = db.Column(db.Integer, nullable=True)

    __table_args__ = (db.UniqueConstraint('channel_id', 'auto_type'),)

    _videos = db.relationship(PlaylistVideo,
        order_by=[PlaylistVideo.seq],
        collection_class=ordering_list('seq'),
        backref='playlist',
        cascade='all, delete-orphan')
    videos = association_proxy('_videos', 'video', creator=lambda x: PlaylistVideo(video=x))

    def type_label(self):
        if self.auto_type is not None:
            return playlist_auto_types.get(self.type)
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
            perms.add('new-video')
            perms.add('remove-video')
        return perms

    def url_for(self, action='view'):
        if action == 'view':
            return url_for('playlist_view', channel=self.channel.name, playlist=self.name)
        elif action == 'edit':
            return url_for('playlist_edit', channel=self.channel.name, playlist=self.name)
        elif action == 'delete':
            return url_for('playlist_delete', channel=self.channel.name, playlist=self.name)
        elif action == 'new-video':
            return url_for('video_new', channel=self.channel.name, playlist=self.name)
        # The remove-video view URL is in Video, not here. Only the permission comes from here.
