#!/usr/bin/env python
from hgtv import app
from hgtv.models import db
db.create_all()
app.run(debug=True, port=8000)
