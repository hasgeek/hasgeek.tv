# -*- coding: utf-8 -*-

from flask import render_template
from coaster.views import load_model

from hgtv import app
from hgtv.models import Channel


@app.route('/<channel>/')
@load_model(Channel, {'name': 'channel'}, 'channel')
def channel_view(channel):
    return render_template('channel.html', channel=channel)
