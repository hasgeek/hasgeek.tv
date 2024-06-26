# The imports in this file are order-sensitive

from flask import Flask
from flask_migrate import Migrate
from pytz import timezone

import coaster.app
from baseframe import Version, baseframe
from flask_lastuser import Lastuser
from flask_lastuser.sqlalchemy import UserManager

from ._version import __version__

version = Version(__version__)
app = Flask(__name__, instance_relative_config=True)
lastuser = Lastuser()


from . import models, uploads, views  # NOQA
from .models import db

# Configure the app
coaster.app.init_app(app, ['py', 'env'], env_prefix=['FLASK', 'APP_HGTV'])
db.init_app(app)
db.app = app  # type: ignore[attr-defined]
migrate = Migrate(app, db)
baseframe.init_app(
    app,
    requires=['baseframe-mui'],
    theme='mui',
)
lastuser.init_app(app)
lastuser.init_usermanager(UserManager(db, models.User))
app.config['tz'] = timezone(app.config['TIMEZONE'])
uploads.configure(app)
