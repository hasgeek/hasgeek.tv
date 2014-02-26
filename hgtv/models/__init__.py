# -*- coding: utf-8 -*-

from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.commentease import Commentease
from coaster.utils import LabeledEnum
from coaster.sqlalchemy import TimestampMixin, BaseMixin, BaseNameMixin, BaseScopedNameMixin, BaseIdNameMixin
from hgtv import app

db = SQLAlchemy(app)
commentease = Commentease(db=db)


class PLAYLIST_AUTO_TYPE(LabeledEnum):
    WATCHED = (1, u"Watched")
    STARRED = (2, u"Starred")
    LIKED = (3, u"Liked")
    DISLIKED = (4, u"Disliked")
    SPEAKING_IN = (5, u"Speaking in")
    APPEARING_IN = (6, u"Appearing in")
    CREW_IN = (7, u"Crew in")
    ATTENDED = (8, u"Attended")
    QUEUE = (9, u"Queue")
    STREAM = (10, u"All videos")


from hgtv.models.video import *
from hgtv.models.channel import *
from hgtv.models.user import *
from hgtv.models.tag import *
