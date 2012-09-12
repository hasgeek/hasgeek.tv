# -*- coding: utf-8 -*-

from flask import render_template, g, flash, jsonify, request, abort, escape, url_for
from coaster.views import load_model
from baseframe.forms import render_redirect, render_form

from hgtv import app
from hgtv.views.login import lastuser
from hgtv.forms import ChannelForm, VideoCsrfForm
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


@app.route('/<channel>/user_playlists', methods=['GET'])
@load_model(Channel, {'name': 'channel'}, 'channel', permission='new-playlist')
@lastuser.requires_login
def playlist_all(channel):
    """
    Return list of all playlist for the channel in html.
    """
    if request.is_xhr and request.method == 'GET' and request.args.get('csrf_token'):
        video = Video.query.filter_by(name=unicode(request.args.get('video_name'))).first()
        html_to_return = "<ul class='dropdown-menu'>"
        for index, p in enumerate(channel.user_playlists):
            html_to_return += "<li><a href='#' id='playlist-item'"
            if index is 0:
                html_to_return += "data='" + p.name + "'>" + channel.title + " &raquo;"
                if p.short_title:
                    html_to_return += p.short_title
                else:
                    html_to_return += "<br>" + p.title
                if video in p.videos:
                    html_to_return += " <i class='icon-ok'></i>"
            else:
                html_to_return += "data='" + p.name + "'>" + p.title
                if video in p.videos:
                    html_to_return += " <i class='icon-ok'></i>"
                html_to_return += "</a></li>"
        html_to_return += u"""<li class='divider'></li><li>
            <a href="#" class="button" data-backdrop="true" data-controls-modal="event-modal" data-keyboard="true" id='playlist-item'
            data="new-playlist">Add Playlist</a></li></ul>
            """
        return jsonify({'html': html_to_return, 'message_type': 'success', 'action': 'append'})
    abort(403)


@app.route('/<channel>/action', methods=['POST'])
@lastuser.requires_login
@load_model(Channel, {'name': 'channel'}, 'channel', permission='new-playlist')
def channel_action(channel):
    """
    Perform an action in the channel
    """
    form = VideoCsrfForm()
    video_name = unicode(escape(request.form.get('video_name')))
    playlist_name = unicode(escape(request.form.get('playlist_name')))
    if video_name and playlist_name and form.validate():
        video = Video.query.filter_by(name=video_name).first()
        playlist = Playlist.query.filter_by(name=playlist_name).first()
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
                to_return = {'message_type': message_type, 'action': action, 'message': message, 'playlist_name': playlist_name}
            else:
                playlist.videos.append(video)
                to_return = {'message_type': 'success', 'action': 'add',
                    'message': u"Video successfully added to playlist", 'playlist_name': playlist_name}
        else:
            to_return = {'message_type': 'error', 'action': 'add',
                    'message': u"Video doesn't exist", 'playlist_name': playlist_name}
        db.session.commit()
        return jsonify(to_return)
    abort(403)
