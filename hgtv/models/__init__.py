# flake8: noqa

from __future__ import annotations

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

from baseframe import __
from coaster.sqlalchemy import (
    BaseIdNameMixin,
    BaseMixin,
    BaseNameMixin,
    BaseScopedNameMixin,
    ModelBase,
    Query,
    TimestampMixin,
    backref,
    relationship,
)
from coaster.utils import LabeledEnum

from .. import app

TimestampMixin.__with_timezone__ = True


class Model(ModelBase, DeclarativeBase):
    """Base class for models."""


db = SQLAlchemy(
    metadata=Model.metadata,
    query_class=Query,  # type: ignore[arg-type]
)
Model.init_flask_sqlalchemy(db)


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


from .channel import *
from .tag import *
from .user import *
from .video import *
