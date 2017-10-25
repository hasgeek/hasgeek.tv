# -*- coding: utf-8 -*-

from flask import jsonify, url_for
from coaster.views import render_with
from baseframe.forms import render_message
from hgtv import app
from hgtv.models import Channel

from pytz import utc


@app.template_filter('shortdate')
def shortdate(date):
    return utc.localize(date).astimezone(app.config['tz']).strftime('%e %b')


@app.template_filter('longdate')
def longdate(date):
    return utc.localize(date).astimezone(app.config['tz']).strftime('%e %B %Y')


def jsonify_channel(data):
    channels_dicts = []
    for channel in data['channels']:
        channels_dicts.append({
            'url': channel.url_for(),
            'title': channel.title,
            'logo': url_for('static', filename='thumbnails/' + channel.channel_logo_filename) if channel.channel_logo_filename else url_for('static', filename='img/sample-logo.png'),
            'banner_url': channel.channel_banner_url if channel.channel_banner_url else "",
            'bio': channel.bio if channel.bio else ""
        })
    return jsonify(channels=channels_dicts)


@app.route('/')
@render_with({'text/html': 'index.html.jinja2', 'application/json': jsonify_channel})
def index():
    return dict(channels=Channel.get_featured())


@app.route('/search')
def search():
    return render_message(title="No search", message=u"Search hasn’t been implemented yet.")
