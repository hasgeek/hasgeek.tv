# -*- coding: utf-8 -*-
# flake8: noqa

from baseframe import __
from coaster.db import db
from coaster.sqlalchemy import (
    BaseIdNameMixin,
    BaseMixin,
    BaseNameMixin,
    BaseScopedNameMixin,
    TimestampMixin,
)
from coaster.utils import LabeledEnum
from flask_sqlalchemy import SQLAlchemy

from hgtv import app

TimestampMixin.__with_timezone__ = True


class PLAYLIST_AUTO_TYPE(LabeledEnum):
    WATCHED = (1, 'watched', __("Watched"))
    STARRED = (2, 'starred', __("Starred"))
    LIKED = (3, 'liked', __("Liked"))
    DISLIKED = (4, 'disliked', __("Disliked"))
    SPEAKING_IN = (5, 'speaking-in', __("Speaking in"))
    APPEARING_IN = (6, 'appearing-in', __("Appearing in"))
    CREW_IN = (7, 'crew-in', __("Crew in"))
    ATTENDED = (8, 'attended', __("Attended"))
    QUEUE = (9, 'queue', __("Queue"))
    STREAM = (10, 'stream', __("All videos"))


from hgtv.models.channel import *
from hgtv.models.tag import *
from hgtv.models.user import *
from hgtv.models.video import *
