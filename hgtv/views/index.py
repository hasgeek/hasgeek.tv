# -*- coding: utf-8 -*-

from flask import render_template
from baseframe.forms import render_message
from hgtv import app
from hgtv.models import Channel, Video

from pytz import utc


@app.template_filter('shortdate')
def shortdate(date):
    return utc.localize(date).astimezone(app.config['tz']).strftime('%b %e')


@app.template_filter('longdate')
def longdate(date):
    return utc.localize(date).astimezone(app.config['tz']).strftime('%B %e, %Y')


@app.route('/')
def index():
    return render_template('index.html', channels=Channel.get_featured(), videos=Video.get_featured())


@app.route('/search')
def search():
    return render_message(title="No search", message=u"Search hasn’t been implemented yet.")
