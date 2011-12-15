# -*- coding: utf-8 -*-

# The imports in this file are order-sensitive

from flask import Flask
from flaskext.assets import Environment, Bundle
from baseframe import baseframe, baseframe_js, baseframe_css
from coaster import configureapp

# First, make an app and config it

app = Flask(__name__, instance_relative_config=True)
configureapp(app, 'HGTV_SETTINGS')
# Second, setup baseframe and assets

app.register_blueprint(baseframe)
assets = Environment(app)
js = Bundle(baseframe_js)
css = Bundle(baseframe_css)
assets.register('js_all', js)
assets.register('css_all', css)

# Third, after config, import the models and views

import hgtv.models
import hgtv.views

# Fourth, setup admin for the models

from flask.ext import admin
from sqlalchemy.orm import scoped_session, sessionmaker
from hgtv.views.login import lastuser

db_session = scoped_session(sessionmaker(
    autocommit=False, autoflush=False,
    bind=hgtv.models.db.engine))

admin_blueprint = admin.create_admin_blueprint(
     hgtv.models, db_session,
     view_decorator=lastuser.requires_permission('siteadmin'))

app.register_blueprint(admin_blueprint, url_prefix='/admin')
