# -*- coding: utf-8 -*-

from flaskext.sqlalchemy import SQLAlchemy
from hgtv import app
from coaster.sqlalchemy import IdMixin, TimestampMixin, BaseMixin, BaseNameMixin

db = SQLAlchemy(app)

from hgtv.models.user import *
from hgtv.models.tag import *
