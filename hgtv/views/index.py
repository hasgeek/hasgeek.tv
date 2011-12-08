# -*- coding: utf-8 -*-

import os
from flask import g, send_from_directory, Response, get_flashed_messages, flash
from hgtv import app

@app.route('/')
def index():
    resp = []
    for category, msg in get_flashed_messages(with_categories=True):
        resp.append(u'-- %s: %s --' % (category, msg))
    if g.user:
        resp.append(u'User: %s' % g.user)
    resp.append(u"HasGeek.tv. Come back later.")
    return Response(u'\n'.join(resp), mimetype="text/plain")


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')
