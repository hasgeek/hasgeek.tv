# -*- coding: utf-8 -*-

from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.commentease import Commentease
from coaster.sqlalchemy import TimestampMixin, BaseMixin, BaseNameMixin, BaseScopedNameMixin, BaseIdNameMixin
from hgtv import app

db = SQLAlchemy(app)
commentease = Commentease(db=db)

class PLAYLIST_AUTO_TYPE:
    WATCHED = 1
    STARRED = 2
    LIKED = 3
    DISLIKED = 4
    SPEAKING_IN = 5
    APPEARING_IN = 6
    CREW_IN = 7
    ATTENDED = 8
    QUEUE = 9
    STREAM = 10

playlist_auto_types = {
    1: u"Watched",
    2: u"Starred",
    3: u"Liked",
    4: u"Disliked",
    5: u"Speaking in",
    6: u"Appearing in",
    7: u"Crew in",
    8: u"Attended",
    9: u"Queue",
    10: u"Stream",
}

from hgtv.models.video import *
from hgtv.models.channel import *
from hgtv.models.user import *
from hgtv.models.tag import *
