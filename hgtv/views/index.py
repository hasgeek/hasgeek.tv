# -*- coding: utf-8 -*-

from flask import render_template
from baseframe.forms import render_message
from hgtv import app
from hgtv.models import Playlist

from pytz import utc


@app.template_filter('shortdate')
def shortdate(date):
    return utc.localize(date).astimezone(app.config['tz']).strftime('%b %e')


@app.template_filter('longdate')
def longdate(date):
    return utc.localize(date).astimezone(app.config['tz']).strftime('%B %e, %Y')


@app.route('/')
def index():
    playlists = Playlist.get_featured(10)
    return render_template('index.html', playlists=playlists)


@app.route('/search')
def search():
    return render_message(title="No search", message=u"Search hasn’t been implemented yet.")
