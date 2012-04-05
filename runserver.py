#!/usr/bin/env python
from hgtv import app
from hgtv.models import db
db.create_all()
app.run('0.0.0.0', debug=True, port=8000)
