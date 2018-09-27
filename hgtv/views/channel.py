# -*- coding: utf-8 -*-

import os
from flask import render_template, g, jsonify, request, make_response
from coaster.views import load_model, load_models, render_with
from baseframe import _
from baseframe.forms import render_form

from hgtv import app
from hgtv.views.login import lastuser
from hgtv.views.video import VideoAddForm, DataProcessingError, process_video, process_slides
from hgtv.forms import ChannelForm, PlaylistForm
from hgtv.models import Channel, db, Playlist, Video, CHANNEL_TYPE
from hgtv.uploads import thumbnails, resize_image


@app.route('/<channel>/')
@render_with({'text/html': 'index.html.jinja2'}, json=True)
@load_model(Channel, {'name': 'channel'}, 'channel', permission='view')
def channel_view(channel):
    playlist_list = [playlist.current_access_with_featured_videos() for playlist in channel.playlists]
    return {'channel': dict(channel.current_access()), 'playlists': playlist_list}


@app.route('/<channel>/edit', methods=['GET', 'POST'])
@lastuser.requires_login
@render_with({'text/html': 'index.html.jinja2'}, json=True)
@load_model(Channel, {'name': 'channel'}, 'channel', permission='edit')
def channel_edit(channel):
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
        html_form = render_form(form=form, title=_("Edit channel"), submit=_("Save"),
        cancel_url=channel.url_for(), ajax=False, with_chrome=False)
        return {'channel': dict(channel.current_access()), 'form': html_form}
    if form.validate_on_submit():
        old_channel = channel
        form.populate_obj(channel)
        if form.delete_logo and form.delete_logo.data:
            try:
                if old_channel.channel_logo_filename:
                    os.remove(os.path.join(app.static_folder, 'thumbnails', old_channel.channel_logo_filename))
                    message = "Removed channel logo"
            except OSError:
                channel.channel_logo_filename = None
                message = "Channel logo already Removed"
        else:
            if 'channel_logo' in request.files and request.files['channel_logo']:
                try:
                    if old_channel.channel_logo_filename:
                        db.session.add(old_channel)
                        try:
                            os.remove(os.path.join(app.static_folder, 'thumbnails', old_channel.channel_logo_filename))
                        except OSError:
                            old_channel.channel_logo_filename = None
                            message = "Unable to delete previous logo"
                    image = resize_image(request.files['channel_logo'])
                    channel.channel_logo_filename = thumbnails.save(image)
                    message = "Channel logo uploaded"
                except OSError:
                    message = "Unable to save image"
                    channel.channel_logo_filename = None
            else:
                message = "Edited description for channel"
        db.session.commit()
        return {'status': 'ok', 'doc': _(message), 'result': {}}
    return {'status': 'error', 'errors': form.errors}, 400


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
@render_with({'text/html': 'index.html.jinja2'}, json=True)
@load_models(
    (Channel, {'name': 'channel'}, 'channel'),
    (Video, {'url_name': 'video'}, 'video'), permission='new-playlist')
def playlist_new_modal(channel, video):
    # Make a new playlist
    form = PlaylistForm()
    if request.method == 'GET':
        html_form = render_form(form=form, title=_("New Playlist"), submit=_("Save"),
        cancel_url=channel.url_for(), ajax=False, with_chrome=False)
        return {'channel': dict(channel.current_access()), 'form': html_form}
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
            message = "Added video to playlist"
        else:
            message = "This video is already in that playlist"
        db.session.commit()
        return {'status': 'ok', 'doc': _(message), 'result': {'new_playlist_url': playlist.url_for()}}, 201
    return {'status': 'error', 'errors': form.errors}, 400


@app.route('/<channel>/new/stream', methods=['GET', 'POST'])
@lastuser.requires_login
@render_with({'text/html': 'index.html.jinja2'}, json=True)
@load_models(
    (Channel, {'name': 'channel'}, 'channel'),
    permission='new-video')
def stream_new_video(channel):
    """
    Add a new video to stream playlist
    """
    form = VideoAddForm()
    if request.method == 'GET':
        cancel_url = channel.url_for()
        html_form = render_form(form=form, title=_("New Video"), submit=_("Add"),
                           cancel_url=cancel_url, ajax=False, with_chrome=False)
        return {'channel': dict(channel.current_access()), 'form': html_form}
    if form.validate_on_submit():
        stream_playlist = channel.playlist_for_stream(create=True)
        video = Video(playlist=stream_playlist)
        form.populate_obj(video)
        try:
            process_video(video, new=True)
            process_slides(video)
        except (DataProcessingError, ValueError) as e:
            return {'status': 'error', 'errors': {'error': [e.message]}}, 400
        video.make_name()
        if video not in stream_playlist.videos:
            stream_playlist.videos.append(video)
        db.session.commit()
        return {'status': 'ok', 'doc': _("Added video {title}.".format(title=video.title)), 'result': {'new_video_edit_url': video.url_for('edit')}}, 201
    else:
        return {'status': 'error', 'errors': form.errors}, 400
