# -*- coding: utf-8 -*-

import os
from flask import render_template, g, jsonify, request, make_response
from coaster.views import load_model, load_models, render_with, ClassView
from baseframe import _
from baseframe.forms import render_form

from hgtv import app
from hgtv.views.login import lastuser
from hgtv.views.video import add_new_video
from hgtv.forms import ChannelForm, PlaylistForm
from hgtv.models import Channel, db, Playlist, Video, CHANNEL_TYPE
from hgtv.uploads import thumbnails, resize_image


@app.route('/<channel>/')
@render_with({'text/html': 'index.html.jinja2'}, json=True)
@load_model(Channel, {'name': 'channel'}, 'channel', permission='view')
def channel_view(channel):
    playlist_list = [playlist.current_access_featured_videos() for playlist in channel.playlists]
    return dict(channel=dict(channel.current_access()), playlists=playlist_list)


def jsonify_edit_channel(data):
    channel = data['channel']
    form = ChannelForm(obj=channel)
    if channel.userid == g.user.userid:
        form.type.choices = [(1, CHANNEL_TYPE[1])]
    else:
        choices = CHANNEL_TYPE.items()
        choices.pop(0)
        choices.pop(0)
        form.type.choices = choices
    if not channel.channel_logo_filename:
        del form.delete_logo
    if request.method == 'GET':
        html_form = render_form(form=form, title=u"Edit channel", submit=u"Save",
        cancel_url=channel.url_for(), ajax=False, with_chrome=False)
        return jsonify(channel=dict(channel.current_access()), form=html_form)
    if form.validate_on_submit():
        old_channel = channel
        form.populate_obj(channel)
        if form.delete_logo and form.delete_logo.data:
            try:
                if old_channel.channel_logo_filename:
                    os.remove(os.path.join(app.static_folder, 'thumbnails', old_channel.channel_logo_filename))
            except OSError:
                channel.channel_logo_filename = None
        else:
            if 'channel_logo' in request.files and request.files['channel_logo']:
                try:
                    if old_channel.channel_logo_filename:
                        db.session.add(old_channel)
                        try:
                            os.remove(os.path.join(app.static_folder, 'thumbnails', old_channel.channel_logo_filename))
                        except OSError:
                            old_channel.channel_logo_filename = None
                    image = resize_image(request.files['channel_logo'])
                    channel.channel_logo_filename = thumbnails.save(image)
                except OSError:
                    channel.channel_logo_filename = None
        db.session.commit()
        return make_response(jsonify(status='ok', doc=_(u"Edited channel {title}.".format(title=channel.title)), result={}), 200)
    return make_response(jsonify(status='error', errors=form.errors), 400)


@app.route('/<channel>/edit', methods=['GET', 'POST'])
@lastuser.requires_login
@render_with({'text/html': 'index.html.jinja2', 'application/json': jsonify_edit_channel})
@load_model(Channel, {'name': 'channel'}, 'channel')
def channel_edit(channel):
    return dict(channel=channel)


@app.route('/_embed/user_playlists/<video>', methods=['GET'])
@lastuser.requires_login
@load_model(Video, {'url_name': 'video'}, 'video')
def user_playlists(video):
    """
    Return list of all playlist for the channel in html.
    """
    html = render_template('playlist-menu.html.jinja2', user=g.user, video=video)
    if request.is_xhr:
        return jsonify(html=html, message_type='success', action='append')
    else:
        return html


@app.route('/<channel>/new_playlist_ajax/<video>', methods=['POST', 'GET'])
@lastuser.requires_login
@load_models(
    (Channel, {'name': 'channel'}, 'channel'),
    (Video, {'url_name': 'video'}, 'video'), permission='new-playlist')
def playlist_new_modal(channel, video):
    # Make a new playlist
    form = PlaylistForm()
    html = render_template('playlist-modal.html.jinja2', form=form, channel=channel, video=video)
    if request.is_xhr:
        if form.validate_on_submit():
            playlist = Playlist(channel=channel)
            form.populate_obj(playlist)
            if not playlist.name:
                playlist.make_name()
            db.session.add(playlist)
            stream_playlist = channel.playlist_for_stream(create=True)
            if video not in stream_playlist.videos:
                stream_playlist.videos.append(video)
            if video not in playlist.videos:
                playlist.videos.append(video)
                message = u"Added video to playlist"
                message_type = 'success'
                action = 'append'
            else:
                message = u"This video is already in that playlist"
                message_type = 'info'
                action = 'noop'
            html_to_return = render_template('new-playlist-tag.html.jinja2', playlist=playlist, channel=channel, video=video)
            db.session.commit()
            return jsonify({'html': html_to_return, 'message_type': message_type, 'action': action,
                'message': message})
        if form.errors:
            html = render_template('playlist-modal.html.jinja2', form=form, channel=channel, video=video)
            return jsonify({'message_type': "error", 'action': 'append',
                'html': html})
        return jsonify({'html': html, 'message_type': 'success', 'action': 'modal-window'})
    return html


@app.route('/<channel>/new/stream', methods=['GET', 'POST'])
@lastuser.requires_login
@render_with({'text/html': 'index.html.jinja2', 'application/json': add_new_video})
@load_models(
    (Channel, {'name': 'channel'}, 'channel'),
    permission='new-video')
def stream_new_video(channel):
    """
    Add a new video to stream playlist
    """
    return dict(channel=channel, playlist=None)
