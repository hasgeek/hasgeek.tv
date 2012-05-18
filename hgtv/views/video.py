# -*- coding: utf-8 -*-

from flask import render_template, url_for, g, flash, abort, redirect, Markup, request
from coaster.views import load_models
from baseframe.forms import render_form, render_redirect, render_delete_sqla, render_message

from hgtv import app
from hgtv.forms import VideoAddForm, VideoEditForm, PlaylistAddForm
from hgtv.models import Channel, Video, Playlist, PlaylistVideo, db
from hgtv.views.login import lastuser

from urlparse import urlparse, parse_qs


@app.route('/<channel>/<playlist>/new', methods=['GET', 'POST'])
@lastuser.requires_login
@load_models((Channel, {'name': 'channel'}, 'channel'),
             (Playlist, {'name': 'playlist', 'channel': 'channel'}, 'playlist'))
def video_new(channel, playlist):
    """
    Add a new video
    """
    if channel.userid not in g.user.user_organization_ids():
        """
        User doesn't own this playlist
        """
        abort(403)

    form = VideoAddForm()
    if form.validate_on_submit():
        video = Video(playlist=playlist)
        form.populate_obj(video)
        video.process_video()
        video.process_slides()
        video.make_name()
        db.session.add(video)
        playlist.videos.append(video)
        db.session.commit()
        flash(u"Added video '%s'." % video.title, 'success')
        return render_redirect(url_for('video_view', channel=channel.name, playlist=playlist.name, video=video.url_name))
    return render_form(form=form, title="New Video", submit="Add", cancel_url=url_for('channel_view', channel=channel.name), ajax=False)


# Use /view as a temp workaround to a Werkzeug URLmap sorting bug
@app.route('/<channel>/<playlist>/<video>/view', methods=['GET', 'POST'])
@load_models(
    (Channel, {'name': 'channel'}, 'channel'),
    (Playlist, {'name': 'playlist', 'channel': 'channel'}, 'playlist'),
    (Video, {'url_name': 'video'}, 'video'),
    kwargs=True)
def video_view(channel, playlist, video, kwargs):
    """
    View video
    """
    if playlist not in video.playlists:
        # This video isn't in this playlist. Redirect to canonical URL
        return redirect(url_for('video_view', channel=video.channel.name, playlist=video.playlist.name, video=video.url_name))

    if kwargs['video'] != video.url_name:
        # Video's URL has changed. Redirect user to prevent old/invalid names
        # showing in the URL
        return redirect(url_for('video_view', channel=channel.name, playlist=playlist.name, video=video.url_name))

    form = PlaylistAddForm()
    playlists = set(channel.playlists) - set(video.playlists)
    form.playlist.choices = [(p.id, p.title) for p in playlists]
    if form.validate_on_submit():
        if channel.userid not in g.user.user_organization_ids():
            abort(403)
        playlist = Playlist.query.get(form.data['playlist'])
        playlist.videos.append(video)
        db.session.commit()
        flash(u"Added video '%s'." % video.title, 'success')
    return render_template('video.html', title=video.title, channel=channel, playlist=playlist, video=video, form=form)


@app.route('/<channel>/<playlist>/<video>/edit', methods=['GET', 'POST'])
@lastuser.requires_login
@load_models(
    (Channel, {'name': 'channel'}, 'channel'),
    (Playlist, {'name': 'playlist', 'channel': 'channel'}, 'playlist'),
    (Video, {'url_name': 'video'}, 'video'),
    kwargs=True)
def video_edit(channel, playlist, video, kwargs):
    """
    Edit video
    """
    if video.channel.userid not in g.user.user_organization_ids():
        # User isn't authorized to edit
        abort(403)

    if playlist != video.playlist:
        # This video isn't in this playlist. Redirect to canonical URL
        return redirect(url_for('video_edit', channel=video.channel.name, playlist=video.playlist.name, video=video.url_name))

    if kwargs['video'] != video.url_name:
        # Video's URL has changed. Redirect user to prevent old/invalid names
        # showing in the URL
        return redirect(url_for('video_delete', channel=channel.name, playlist=playlist.name, video=video.url_name))

    form = VideoEditForm(obj=video)
    if form.validate_on_submit():
        form.populate_obj(video)
        try:
            video.process_slides()
            db.session.commit()
        except ValueError as e:
            return render_form(form=form, title=u"Edit video", submit=u"Save",
                   cancel_url=url_for('video_view', channel=channel.name, playlist=playlist.name, video=video.url_name),
                   message=e, ajax=True)
        flash(u"Edited video '%s'." % video.title, 'success')
        return render_redirect(url_for('video_view', channel=channel.name, playlist=playlist.name, video=video.url_name))
    return render_form(form=form, title=u"Edit video", submit=u"Save",
        cancel_url=url_for('video_view', channel=channel.name, playlist=playlist.name, video=video.url_name),
        ajax=True)


@app.route('/<channel>/<playlist>/<video>/delete', methods=['GET', 'POST'])
@lastuser.requires_login
@load_models(
    (Channel, {'name': 'channel'}, 'channel'),
    (Playlist, {'name': 'playlist', 'channel': 'channel'}, 'playlist'),
    (Video, {'url_name': 'video'}, 'video'),
    kwargs=True)
def video_delete(channel, playlist, video, kwargs):
    """
    Delete video
    """
    if video.channel.userid not in g.user.user_organization_ids():
        # User isn't authorized to delete
        abort(403)

    if playlist != video.playlist:
        # This video isn't in this playlist. Redirect to canonical URL
        return redirect(url_for('video_delete', channel=video.channel.name, playlist=video.playlist.name, video=video.url_name))

    if kwargs['video'] != video.url_name:
        # Video's URL has changed. Redirect user to prevent old/invalid names
        # showing in the URL
        return redirect(url_for('video_delete', channel=channel.name, playlist=playlist.name, video=video.url_name))

    return render_delete_sqla(video, db, title=u"Confirm delete",
        message=u"Delete video '%s'? This will remove the video from all playlists it appears in." % video.title,
        success=u"You have deleted video '%s'." % video.title,
        next=url_for('playlist_view', channel=channel.name, playlist=playlist.name))


@app.route('/<channel>/<playlist>/<video>/remove', methods=['GET', 'POST'])
@lastuser.requires_login
@load_models(
    (Channel, {'name': 'channel'}, 'channel'),
    (Playlist, {'name': 'playlist', 'channel': 'channel'}, 'playlist'),
    (Video, {'url_name': 'video'}, 'video'),
    kwargs=True)
def video_remove(channel, playlist, video, kwargs):
    """
    Remove video from playlist
    """
    if playlist not in video.playlists:
        # This video isn't in this playlist
        abort(404)

    if channel.userid not in g.user.user_organization_ids():
        # User doesn't own this playlist
        abort(403)

    if kwargs['video'] != video.url_name:
        # Video's URL has changed. Redirect user to prevent old/invalid names
        # showing in the URL
        return redirect(url_for('video_remove', channel=channel.name, playlist=playlist.name, video=video.url_name))

    # If this is the primary playlist for this video, refuse to remove it.
    if playlist == video.playlist:
        return render_message(title="Cannot remove",
            message=Markup("Videos cannot be removed from their primary playlist. "
                '<a href="%s">Return to video</a>.' % url_for('video_view',
                    channel=channel.name, playlist=playlist.name, video=video.url_name)))

    connection = PlaylistVideo.query.filter_by(playlist_id=playlist.id, video_id=video.id).first_or_404()

    return render_delete_sqla(connection, db, title="Confirm remove",
        message=u"Remove video '%s' from playlist '%s'?" % (video.title, playlist.title),
        success=u"You have removed video '%s' from playlist '%s'." % (video.title, playlist.title),
        next=url_for('playlist_view', channel=channel.name, playlist=playlist.name))

