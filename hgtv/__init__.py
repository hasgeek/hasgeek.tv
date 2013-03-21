# -*- coding: utf-8 -*-

# The imports in this file are order-sensitive

from pytz import timezone
from flask import Flask
from flask.ext.lastuser import Lastuser
from flask.ext.lastuser.sqlalchemy import UserManager
from baseframe import baseframe
import coaster.app
from coaster.assets import Version
from baseframe.assets import assets
from ._version import *

# First, make an app

app = Flask(__name__, instance_relative_config=True)
lastuser = Lastuser()

# Second, setup baseframe and assets

app.register_blueprint(baseframe)

version = Version(__version__)
assets['presentz.js'][version] = 'js/presentz-1.2.0.js'
assets['hgtv.css'][version] = 'css/app.css'

# Third, after config, import the models and views

import hgtv.models
import hgtv.views
import hgtv.uploads
from hgtv.models import db


def init_for(env):
    coaster.app.init_app(app, env)
    baseframe.init_app(app, requires=['baseframe', 'hgtv', 'presentz'])
    hgtv.models.commentease.init_app(app)
    lastuser.init_app(app)
    lastuser.init_usermanager(UserManager(hgtv.models.db, hgtv.models.User))
    app.config['tz'] = timezone(app.config['TIMEZONE'])
    hgtv.uploads.configure(app)
