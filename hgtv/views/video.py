# -*- coding: utf-8 -*-

from flask import render_template, redirect, url_for
from coaster.views import load_model

from hgtv import app
from hgtv.models import Channel, Video


@app.route('/<channel>/view/')
@load_model(Channel, {'name': 'channel'}, 'channel')
def video_namespace(channel):
    return redirect(url_for('channel', channel=channel.name))


@app.route('/<channel>/view/<video>')
@load_model([
    (Channel, {'name': 'channel'}, 'channel'),
    (Video, {'name': 'video', 'channel': 'channel'}, 'video')
    ])
def video_view(channel, video):
    return render_template('video.html', channel=channel, video=video)
