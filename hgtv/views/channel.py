# -*- coding: utf-8 -*-

import os
from werkzeug import secure_filename
from flask import render_template, g, flash, jsonify, request
from coaster.views import load_model, load_models
from baseframe.forms import render_form, render_redirect

from hgtv import app
from hgtv.views.login import lastuser
from hgtv.views.video import process_video, process_slides, add_new_video, DataProcessingError
from hgtv.forms import ChannelForm, PlaylistForm, VideoAddForm
from hgtv.models import Channel, db, Playlist, Video
from hgtv.models.channel import channel_types
from hgtv.uploads import thumbnails, resize_image


@app.route('/<channel>/')
@load_model(Channel, {'name': 'channel'}, 'channel', permission='view')
def channel_view(channel):
    return render_template('channel.html', channel=channel)


@app.route('/<channel>/edit', methods=['GET', 'POST'])
@lastuser.requires_login
@load_model(Channel, {'name': 'channel'}, 'channel', permission='edit')
def channel_edit(channel):
    form = ChannelForm(obj=channel)
    if channel.userid == g.user.userid:
        form.type.choices = [(1, channel_types[1])]
    else:
        choices = channel_types.items()
        choices.sort()
        choices.pop(0)
        choices.pop(0)
        form.type.choices = choices
    if not channel.channel_logo_filename:
        del form.delete_logo
    if form.validate_on_submit():
        old_channel = channel
        form.populate_obj(channel)
        if form.delete_logo and form.delete_logo.data:
            try:
                if old_channel.channel_logo_filename:
                    os.remove(os.path.join(app.static_folder, 'thumbnails', old_channel.channel_logo_filename))
                    flash(u"Removed channel logo", u"success")
                else:
                    flash(u"Channel doesn't have logo", u"info")
            except OSError:
                flash(u"Channel logo already Removed", u"info")
            channel.channel_logo_filename = u""
        else:
            if request.files['channel_logo']:
                try:
                    if not old_channel.channel_logo_filename == u"":
                        db.session.add(old_channel)
                        try:
                            os.remove(os.path.join(app.static_folder, 'thumbnails', channel.channel_logo_filename))
                        except OSError:
                            old_channel.channel_logo_filename = u""
                            flash(u"Unable to delete previous logo", u"error")
                    message = u"Unable to save image"
                    image = resize_image(request.files['channel_logo'])
                    channel.channel_logo_filename = thumbnails.save(image)
                    message = u"Channel logo uploaded"
                except OSError:
                    flash(message, u"error")
            else:
                message = u"Edited description for channel"
                channel.channel_logo_filename = u''
            flash(message, 'success')
        db.session.commit()
        return render_redirect(channel.url_for(), code=303)
    return render_form(form=form, title=u"Edit channel", submit=u"Save",
        cancel_url=channel.url_for(), ajax=False)


@app.route('/_embed/user_playlists/<video>', methods=['GET'])
@lastuser.requires_login
@load_model(Video, {'url_name': 'video'}, 'video')
def user_playlists(video):
    """
    Return list of all playlist for the channel in html.
    """
    html = render_template('playlist-menu.html', user=g.user, video=video)
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
    html = render_template('playlist-modal.html', form=form, channel=channel, video=video)
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
            html_to_return = render_template('new-playlist-tag.html', playlist=playlist, channel=channel, video=video)
            db.session.commit()
            return jsonify({'html': html_to_return, 'message_type': message_type, 'action': action,
                'message': message})
        if form.errors:
            html = render_template('playlist-modal.html', form=form, channel=channel, video=video)
            return jsonify({'message_type': "error", 'action': 'append',
                'html': html})
        return jsonify({'html': html, 'message_type': 'success', 'action': 'modal-window'})
    return html


@app.route('/<channel>/new/stream', methods=['GET', 'POST'])
@lastuser.requires_login
@load_models(
    (Channel, {'name': 'channel'}, 'channel'),
    permission='new-video')
def stream_new_video(channel):
    """
    Add a new video to stream playlist
    """
    return add_new_video(channel, playlist=None)
