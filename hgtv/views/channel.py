# -*- coding: utf-8 -*-

from flask import render_template, g, flash, jsonify, request
from coaster.views import load_model, load_models
from baseframe.forms import render_form, render_redirect

from hgtv import app
from hgtv.views.login import lastuser
from hgtv.views.video import process_video, process_slides, add_new_video, DataProcessingError
from hgtv.forms import ChannelForm, PlaylistForm, VideoAddForm
from hgtv.models import Channel, db, Playlist, Video
from hgtv.models.channel import channel_types


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
    if form.validate_on_submit():
        form.populate_obj(channel)
        db.session.commit()
        flash(u"Edited description for channel", 'success')
        return render_redirect(channel.url_for(), code=303)
    return render_form(form=form, title=u"Edit channel", submit=u"Save",
        cancel_url=channel.url_for(), ajax=True)


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
