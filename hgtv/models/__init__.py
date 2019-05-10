# -*- coding: utf-8 -*-
# flake8: noqa

from flask_sqlalchemy import SQLAlchemy
from coaster.utils import LabeledEnum
from coaster.sqlalchemy import TimestampMixin, BaseMixin, BaseNameMixin, BaseScopedNameMixin, BaseIdNameMixin
from coaster.db import db
from baseframe import __
from hgtv import app


class PLAYLIST_AUTO_TYPE(LabeledEnum):
    WATCHED      = (1,  u'watched',      __(u"Watched"))
    STARRED      = (2,  u'starred',      __(u"Starred"))
    LIKED        = (3,  u'liked',        __(u"Liked"))
    DISLIKED     = (4,  u'disliked',     __(u"Disliked"))
    SPEAKING_IN  = (5,  u'speaking-in',  __(u"Speaking in"))
    APPEARING_IN = (6,  u'appearing-in', __(u"Appearing in"))
    CREW_IN      = (7,  u'crew-in',      __(u"Crew in"))
    ATTENDED     = (8,  u'attended',     __(u"Attended"))
    QUEUE        = (9,  u'queue',        __(u"Queue"))
    STREAM       = (10, u'stream',       __(u"All videos"))


from hgtv.models.video import *
from hgtv.models.channel import *
from hgtv.models.user import *
from hgtv.models.tag import *
