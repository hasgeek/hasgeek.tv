# -*- coding: utf-8 -*-

import os
from flask import g, send_from_directory, Response, get_flashed_messages, flash, render_template
from hgtv import app

@app.route('/')
def index():
    return render_template('index.html')
    resp = []
    for category, msg in get_flashed_messages(with_categories=True):
        resp.append(u'-- %s: %s --' % (category, msg))
    if g.user:
        resp.append(u'User: %s' % g.user)
    resp.append(u"HasGeek.tv. Come back later.")
    return Response(u'\n'.join(resp), mimetype="text/plain")
