# -*- coding: utf-8 -*-

# The imports in this file are order-sensitive

from pytz import timezone
from flask import Flask
from flask.ext.assets import Environment, Bundle
from flask.ext.lastuser import Lastuser
from flask.ext.lastuser.sqlalchemy import UserManager
from baseframe import baseframe, baseframe_js, baseframe_css, toastr_js, toastr_css
import coaster.app

# First, make an app

app = Flask(__name__, instance_relative_config=True)
lastuser = Lastuser()

# Second, setup baseframe and assets

app.register_blueprint(baseframe)

assets = Environment(app)
js = Bundle(baseframe_js, toastr_js,
    filters='jsmin', output='js/packed.js')
css = Bundle(baseframe_css, toastr_css, 'css/app.css',
    filters='cssmin', output='css/packed.css')
assets.register('js_all', js)
assets.register('css_all', css)

# Third, after config, import the models and views

import hgtv.models
import hgtv.views


def init_for(env):
    coaster.app.init_app(app, env)
    hgtv.models.commentease.init_app(app)
    lastuser.init_app(app)
    lastuser.init_usermanager(UserManager(hgtv.models.db, hgtv.models.User))
    app.config['tz'] = timezone(app.config['TIMEZONE'])
