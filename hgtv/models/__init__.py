# -*- coding: utf-8 -*-

from flask.ext.sqlalchemy import SQLAlchemy
from hgtv import app
from coaster.sqlalchemy import IdMixin, TimestampMixin, BaseMixin, BaseNameMixin

db = SQLAlchemy(app)

from hgtv.models.show import *
from hgtv.models.season import *
from hgtv.models.tag import *
from hgtv.models.user import *
from hgtv.models.video import *
