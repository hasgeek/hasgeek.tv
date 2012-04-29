# -*- coding: utf-8 -*-

import os
from flask import send_from_directory, render_template
from hgtv import app
from hgtv.models import Channel, Playlist

from pytz import utc, timezone

tz = timezone(app.config['TIMEZONE'])


@app.template_filter('shortdate')
def shortdate(date):
    return utc.localize(date).astimezone(tz).strftime('%b %e')


@app.template_filter('longdate')
def longdate(date):
    return utc.localize(date).astimezone(tz).strftime('%B %e, %Y')


@app.route('/')
def index():
    channels = Channel.query.order_by('featured').order_by('updated_at').limit(3).all()
    playlists = Playlist.query.order_by('featured').order_by('updated_at').limit(3).all()
    return render_template('index.html', channels=channels, playlists=playlists)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static', 'img'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')
