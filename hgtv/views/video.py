# -*- coding: utf-8 -*-

from flask import render_template, url_for, g, flash, abort, redirect, Markup, request, json, escape
from coaster.views import load_models
from baseframe.forms import render_form, render_redirect, render_delete_sqla, render_message

from hgtv import app
from hgtv.forms import VideoAddForm, VideoEditForm, VideoVideoForm, VideoSlidesForm, PlaylistAddForm
from hgtv.models import Channel, Video, Playlist, PlaylistVideo, db
from hgtv.views.login import lastuser
import requests
from urlparse import urlparse, parse_qs


# helpers
def process_video(video, new=False):
    """
        Get metadata for the video from the corresponding site
    """
    # Parse the video url
    if video.video_url:
        parsed = urlparse(video.video_url)
        # Check video source and get corresponding data
        if parsed.netloc in ['youtube.com', 'www.youtube.com']:
            video_id = parse_qs(parsed.query)['v'][0]
            r = requests.get('https://gdata.youtube.com/feeds/api/videos/%s?v=2&alt=json' % video_id)
            data = json.loads(r.text)
            if new:
                video.title = data['entry']['title']['$t']
                video.description = escape(data['entry']['media$group']['media$description']['$t'])
            for item in data['entry']['media$group']['media$thumbnail']:
                if item['yt$name'] == 'mqdefault':
                    video.thumbnail_url = item['url']  # .replace('hqdefault', 'mqdefault')
            video.video_html = '<iframe src="http://www.youtube.com/embed/%s?wmode=transparent&autoplay=1" frameborder="0" allowfullscreen></iframe>' % video_id
        else:
            raise ValueError("Unsupported video site")
    else:
        raise ValueError("Video URL is missing")
    return video


def process_slides(video):
    """
        Get metadata for slides from the corresponding site
    """
    if video.slides_url:
        parsed = urlparse(video.slides_url)
        if parsed.netloc in ['slideshare.net', 'www.slideshare.net']:
            r = requests.get('http://www.slideshare.net/api/oembed/2?url=%s&format=json' % video.slides_url)
            data = json.loads(r.text)
            slides_id = data['slideshow_id']
            video.slides_html = '<iframe src="http://www.slideshare.net/slideshow/embed_code/%s" frameborder="0" marginwidth="0" marginheight="0" scrolling="no"></iframe>' % slides_id
        elif parsed.netloc in ['speakerdeck.com', 'www.speakerdeck.com']:
            r = requests.get('http://speakerdeck.com/oembed.json?url=%s' % video.slides_url)
            data = json.loads(r.text)
            video.slides_html = data['html']
        else:
            video.slides_html = '<iframe src="%s" frameborder="0"></iframe>' % video.slides_url
            raise ValueError("Unsupported slides site")
    else:
        raise ValueError("Slides URL missing")
    return video


@app.route('/<channel>/<playlist>/new', methods=['GET', 'POST'])
@lastuser.requires_login
@load_models((Channel, {'name': 'channel'}, 'channel'),
             (Playlist, {'name': 'playlist', 'channel': 'channel'}, 'playlist'))
def video_new(channel, playlist):
    """
    Add a new video
    """
    if channel.userid not in g.user.user_organizations_owned_ids():
        """
        User doesn't own this playlist
        """
        abort(403)

    form = VideoAddForm()
    if form.validate_on_submit():
        video = Video(playlist=playlist)
        form.populate_obj(video)
        processed_video = process_video(video, new=True)
        processed_video = process_slides(video)
        processed_video.make_name()
        db.session.add(processed_video)
        playlist.videos.append(processed_video)
        db.session.commit()
        flash(u"Added video '%s'." % processed_video.title, 'success')
        return render_redirect(url_for('video_edit', channel=channel.name, playlist=playlist.name, video=processed_video.url_name))
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

    #form = PlaylistAddForm()
    #playlists = set(channel.playlists) - set(video.playlists)
    #form.playlist.choices = [(p.id, p.title) for p in playlists]
    #if form.validate_on_submit():
    #    if channel.userid not in g.user.user_organizations_owned_ids():
    #        abort(403)
    #    playlist = Playlist.query.get(form.data['playlist'])
    #    playlist.videos.append(video)
    #    db.session.commit()
    #    flash(u"Added video '%s'." % video.title, 'success')
    return render_template('video.html', title=video.title, channel=channel, playlist=playlist, video=video)


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
    if video.channel.userid not in g.user.user_organizations_owned_ids():
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
    formvideo = VideoVideoForm(obj=video)
    formslides = VideoSlidesForm(obj=video)
    form_id = request.form.get('form.id')
    if request.method == "POST":
        if form_id == u'video':  # check whether done button is clicked
            if form.validate_on_submit():
                form.populate_obj(video)
                db.session.commit()
                flash(u"Edited video '%s'." % video.title, 'success')
                return render_redirect(url_for('video_view', channel=channel.name, playlist=playlist.name, video=video.url_name))
        elif form_id == u'video_url':  # check video_url was updated
            if formvideo.validate_on_submit():
                formvideo.populate_obj(video)
                updated_video = process_video(video, new=False)
                db.session.add(updated_video)
                db.session.commit()
                return render_redirect(url_for('video_edit', channel=channel.name, playlist=playlist.name, video=updated_video.url_name))
        elif form_id == u'slide_url':  # check slides_url was updated
            if formslides.validate_on_submit():
                formslides.populate_obj(video)
                updated_video = process_slides(video)
                db.session.add(updated_video)
                db.session.commit()
                return render_redirect(url_for('video_edit', channel=channel.name, playlist=playlist.name, video=updated_video.url_name))
    return render_template('videoedit.html',
        channel=channel,
        playlist=playlist,
        video=video,
        form=form,
        formvideo=formvideo,
        formslides=formslides)
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
    if video.channel.userid not in g.user.user_organizations_owned_ids():
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

    if channel.userid not in g.user.user_organizations_owned_ids():
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
