# -*- coding: utf-8 -*-

from flask import render_template, g, flash, jsonify, request, abort, escape, Markup
from coaster.views import load_model, load_models
from baseframe.forms import render_redirect, render_form

from hgtv import app
from hgtv.views.login import lastuser
from hgtv.forms import ChannelForm, VideoCsrfForm, PlaylistForm
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


@app.route('/<channel>/<playlist>/add', methods=['POST'])
@lastuser.requires_login
@load_models(
    (Channel, {'name': 'channel'}, 'channel'),
    (Playlist, {'name': 'playlist', 'channel': 'channel'}, 'playlist'),
    permission='new-video')
def channel_action(channel, playlist):
    """
    Perform an action in the channel
    """
    form = VideoCsrfForm()
    video_name = unicode(escape(request.args.get('video')))
    if video_name and form.validate():
        video = Video.query.filter_by(name=video_name).first()
        if video:
            # if owner deletes the video while other user is viewing the video
            if video in playlist.videos:
                if playlist != video.playlist:
                    playlist.videos.remove(video)
                    action = u'delete'
                    message = u'Video successfully removed from playlist'
                    message_type = u'success'
                else:
                    action = u'info'
                    message = u'Cannot remove video from primary playlist'
                    message_type = u'info'
                to_return = {'message_type': message_type, 'action': action, 'message': message, 'playlist_name': playlist.name}
            else:
                playlist.videos.append(video)
                to_return = {'message_type': 'success', 'action': 'add',
                    'message': u"Video successfully added to playlist", 'playlist_name': playlist.name}
        else:
            to_return = {'message_type': 'error', 'action': 'add',
                    'message': u"Video doesn't exist", 'playlist_name': playlist.name}
        db.session.commit()
        return jsonify(to_return)
    abort(403)


@app.route('/<channel>/new_playlist_ajax/<video>', methods=['POST', 'GET'])
@lastuser.requires_login
@load_models(
    (Channel, {'name': 'channel'}, 'channel'),
    (Video, {'url_name': 'video'}, 'video'), permission='new-playlist')
def playlist_new_modal(channel, video):
    # Make a new playlist
    form = PlaylistForm()
    form.channel = channel
    #form_content = Markup(render_form(form=form, formid="modal-form", title="New Playlist", submit=u"Create",
    #     ajax=True))
    #form_content = render_template('ajaxform.html', form=form)
    html = render_template('playlist-modal.html', form_content=form, channel=channel, video=video)
    if request.is_xhr:
        if form.validate_on_submit():
            playlist = Playlist(channel=channel)
            form.populate_obj(playlist)
            if not playlist.name:
                playlist.make_name()
            db.session.add(playlist)
            db.session.commit()
            html_to_return = render_template('new-playlist-tag.html', playlist=playlist, channel=channel, video=video)
            return jsonify({'html': html_to_return, 'message_type': 'success', 'action': 'append',
                'message': '%s playlist created' % (playlist.name)})
        if form.errors:
            return jsonify({'message_type': "error", 'action': 'append',
                'html': map(lambda x: unicode(x) + u'_error', form.errors.keys())})
        return jsonify(html=html, message_type='success', action='modal-window')
    return html
