# -*- coding: utf-8 -*-

# The imports in this file are order-sensitive

import coaster.app
from baseframe import Version, baseframe
from flask import Flask
from flask_lastuser import Lastuser
from flask_lastuser.sqlalchemy import UserManager
from flask_migrate import Migrate
from pytz import timezone

from ._version import __version__

version = Version(__version__)
app = Flask(__name__, instance_relative_config=True)
lastuser = Lastuser()


from . import models, uploads, views  # NOQA
from .models import db  # NOQA

# Configure the app
coaster.app.init_app(app)
db.init_app(app)
db.app = app
migrate = Migrate(app, db)
baseframe.init_app(
    app,
    requires=['baseframe-mui'],
    theme='mui',
    asset_modules=('baseframe_private_assets',),
)
lastuser.init_app(app)
lastuser.init_usermanager(UserManager(db, models.User))
app.config['tz'] = timezone(app.config['TIMEZONE'])
uploads.configure(app)
