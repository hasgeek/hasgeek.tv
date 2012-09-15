#!/usr/bin/env python
from hgtv import app, init_for
from hgtv.models import db
init_for('development')
db.create_all()
app.run('0.0.0.0', debug=True, port=8000)
