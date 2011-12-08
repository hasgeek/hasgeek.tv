# -*- coding: utf-8 -*-

from flask import Flask
app = Flask(__name__, instance_relative_config=True)

app.config.from_pyfile('settings.py')

import hgtv.models
import hgtv.views
