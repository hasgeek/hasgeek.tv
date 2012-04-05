# -*- coding: utf-8 -*-

from flask import render_template, abort, g, flash, redirect, url_for
from coaster.views import load_model
from baseframe.forms import render_redirect, render_form

from hgtv import app
from hgtv.views.login import lastuser
from hgtv.forms import PlaylistForm
from hgtv.models import db, Channel, Playlist


@app.route('/<channel>/new', methods=['GET', 'POST'])
@load_model(Channel, {'name': 'channel'}, 'channel')
@lastuser.requires_login
def playlist_new(channel):
    if channel.userid != g.user.userid:
        if channel.userid not in [org['userid'] for org in g.lastuserinfo.organizations['owner']]:
            abort(403)
    # Make a new playlist
    form = PlaylistForm()
    if form.validate_on_submit():
        playlist = Playlist(channel=channel)
        form.populate_obj(playlist)
        playlist.make_name()
        db.session.add(playlist)
        db.session.commit()
        flash('Created playlist %s' % playlist.title, 'success')
        return render_redirect(url_for('playlist_view', channel=channel.name, playlist=playlist.name), code=303)
    return render_form(form=form, title="New Playlist", submit=u"Create",
        cancel_url=url_for('channel_view', channel=channel.name))


@app.route('/<channel>/<playlist>')
@load_model([
    (Channel, {'name': 'channel'}, 'channel'),
    (Playlist, {'name': 'playlist', 'channel': 'channel'}, 'playlist')
    ])
def playlist_view(channel, playlist):
    return render_template('playlist.html', channel=channel, playlist=playlist)
