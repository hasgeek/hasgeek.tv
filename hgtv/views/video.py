# -*- coding: utf-8 -*-

from flask import render_template, redirect, url_for, g, flash, abort
from coaster.views import load_model
from baseframe.forms import render_form, render_redirect

from hgtv import app
from hgtv.forms import VideoAddForm, PlaylistAddForm
from hgtv.models import Channel, Video, Playlist, db
from hgtv.views.login import lastuser

from urlparse import urlparse, parse_qs


@app.route('/<channel>/view/')
@load_model(Channel, {'name': 'channel'}, 'channel')
def video_namespace(channel):
    return redirect(url_for('channel', channel=channel.name))


@app.route('/<channel>/view/<video>', methods=['GET', 'POST'])
@load_model([
    (Channel, {'name': 'channel'}, 'channel'),
    (Video, {'name': 'video', 'channel': 'channel'}, 'video')
    ])
def video_view(channel, video):
    form = PlaylistAddForm()
    playlists = set(channel.playlists) - set(video.playlists)
    form.playlist.choices = [(p.id, p.title) for p in playlists]
    if form.validate_on_submit():
        if not g.user:
            abort(403)
        if channel.userid != g.user.userid:
            if channel.userid not in [org['userid'] for org in g.lastuserinfo.organizations['owner']]:
                abort(403)
        playlist = Playlist.query.get(form.data['playlist'])
        video.playlists.append(playlist)
        db.session.add(video)
        db.session.commit()
        flash(u"Added video '%s'." % video.title, 'success')
    video_id = parse_qs(urlparse(video.url).query)['v'][0]
    return render_template('video.html', title=video.title, channel=channel, video=video, video_id=video_id, form=form)

@app.route('/<channel>/video/new', methods=['GET', 'POST'])
@load_model(Channel, {'name': 'channel'}, 'channel')
def video_add(channel):
    if not g.user:
        abort(403)
    if channel.userid != g.user.userid:
        if channel.userid not in [org['userid'] for org in g.lastuserinfo.organizations['owner']]:
            abort(403)
    form = VideoAddForm()
    if form.validate_on_submit():
        video = Video(channel=channel)
        form.populate_obj(video)
        video.get_metadata()
        video.make_name()
        db.session.add(video)
        db.session.commit()
        flash(u"Added video '%s'." % video.title, 'success')
        return render_redirect(url_for('video_view', channel=channel.name, video=video.name))
    return render_form(form=form, title="New Video", submit="Add", cancel_url=url_for('channel_view', channel=channel.name), ajax=True)
