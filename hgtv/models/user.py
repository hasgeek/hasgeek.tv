from flask import url_for
from werkzeug.utils import cached_property

from flask_lastuser.sqlalchemy import UserBase2

from hgtv.models import PLAYLIST_AUTO_TYPE, db
from hgtv.models.channel import Channel

__all__ = ['User']


class User(UserBase2, db.Model):
    __tablename__ = 'user'

    autoplay = db.Column(db.Boolean, default=True, nullable=False)

    @cached_property
    def profile_url(self):
        return url_for('channel_view', channel=self.username or self.userid)

    @cached_property
    def channel(self):
        return Channel.query.filter_by(userid=self.userid).first()

    @cached_property
    def channels(self):
        # Join lists so that the user's personal channel is always the first
        return [self.channel] + Channel.query.filter(
            Channel.userid.in_(self.organizations_owned_ids())
        ).order_by(Channel.title).all()

    def organization_links(self):
        return [
            {
                'link': url_for('channel_view', channel=org['name']),
                'title': org['title'],
            }
            for org in self.organizations_memberof()
        ]

    def get_video_preference(self, video):
        video_flags = {
            'starred': False,
            'queue': False,
            'liked': False,
            'disliked': False,
        }
        for playlist in video.playlists:
            if playlist.auto_type:
                autotype = PLAYLIST_AUTO_TYPE[playlist.auto_type].name
                if autotype in video_flags:
                    video_flags[autotype] = True
        return video_flags
