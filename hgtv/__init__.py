# -*- coding: utf-8 -*-

# The imports in this file are order-sensitive

from flask import Flask
from flask.ext.assets import Environment, Bundle
from baseframe import baseframe, baseframe_js, baseframe_css
from coaster.app import configure

# First, make an app and config it

app = Flask(__name__, instance_relative_config=True)
configure(app, 'HGTV_ENV')

# Second, setup baseframe and assets

app.register_blueprint(baseframe)

assets = Environment(app)
js = Bundle(baseframe_js)
css = Bundle(baseframe_css,
            'css/hgtv.css')
assets.register('js_all', js)
assets.register('css_all', css)

# Third, after config, import the models and views

import hgtv.models
import hgtv.views
