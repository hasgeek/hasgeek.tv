# -*- coding: utf-8 -*-

from flask.ext.sqlalchemy import SQLAlchemy
from hgtv import app
from coaster.sqlalchemy import TimestampMixin, BaseMixin, BaseNameMixin, BaseIdNameMixin

db = SQLAlchemy(app)

from hgtv.models.video import *
from hgtv.models.channel import *
from hgtv.models.user import *
from hgtv.models.tag import *
