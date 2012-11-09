# -*- coding: utf-8 -*-

import re
from urlparse import urlparse, parse_qs
from socket import gaierror
import requests
from werkzeug import secure_filename

from flask import render_template, flash, abort, redirect, Markup, request, escape, jsonify, g
from coaster.views import load_models
from baseframe.forms import render_form, render_redirect, render_delete_sqla, render_message

from hgtv import app
from hgtv.forms import VideoAddForm, VideoEditForm, VideoVideoForm, VideoSlidesForm, VideoActionForm, VideoCsrfForm
from hgtv.models import db, Channel, Video, Playlist, PlaylistVideo, CHANNEL_TYPE
from hgtv.models.channel import PLAYLIST_AUTO_TYPE
from hgtv.views.login import lastuser
from hgtv.upload import uploaded_thumbnails, return_werkzeug_filestorage


class DataProcessingError(Exception):
    pass


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
            try:
                video_id = parse_qs(parsed.query)['v'][0]
                r = requests.get('https://gdata.youtube.com/feeds/api/videos/%s?v=2&alt=json' % video_id)
                if r.json is None:
                    raise DataProcessingError("Unable to fetch data, please check the youtube url")
                else:
                    if new:
                        video.title = r.json['entry']['title']['$t']
                        video.description = escape(r.json['entry']['media$group']['media$description']['$t'])
                for item in r.json['entry']['media$group']['media$thumbnail']:
                    if item['yt$name'] == 'mqdefault':
                        thumbnail_url_request = requests.get(item['url'])
                        filestorage = return_werkzeug_filestorage(thumbnail_url_request, filename=secure_filename(r.json['entry']['title']['$t']))
                        video.thumbnail_url = uploaded_thumbnails.save(filestorage)
                video.video_sourceid = video_id
                video.video_source = u"youtube"
            except requests.ConnectionError:
                raise DataProcessingError("Unable to establish connection")
            except gaierror:
                raise DataProcessingError("Unable to resolve the hostname")
            except KeyError:
                raise DataProcessingError("Supplied youtube URL doesn't contain video information")
        else:
            raise ValueError("Unsupported video site")

    else:
        raise ValueError("Video URL is missing")


def process_slides(video):
    """
    Get metadata for slides from the corresponding site
    """
    if video.slides_url:
        parsed = urlparse(video.slides_url)
        if parsed.netloc in ['slideshare.net', 'www.slideshare.net']:
            try:
                r = requests.get('http://www.slideshare.net/api/oembed/2?url=%s&format=json' % video.slides_url)
                if r.json:
                    video.slides_source = u'slideshare'
                    video.slides_sourceid = r.json['slideshow_id']
                else:
                    raise DataProcessingError("Unable to fetch data, please check the slideshare url")
            except requests.ConnectionError:
                raise DataProcessingError("Unable to establish connection")
            except gaierror:
                raise DataProcessingError("Unable to resolve the URL")
        elif parsed.netloc in ['speakerdeck.com', 'www.speakerdeck.com']:
            try:
                r = requests.get('http://speakerdeck.com/oembed.json?url=%s' % video.slides_url)
                if r.json:
                    video.slides_source = u'speakerdeck'
                    pattern = u'\Wsrc="//speakerdeck.com/embed/([^\s^"]+)'  # pattern to extract slideid from speakerdeck
                    video.slides_sourceid = re.findall(pattern, r.json['html'])[0]
                else:
                    raise ValueError("Unable to fetch data, please check the speakerdeck URL")
            except requests.ConnectionError:
                raise DataProcessingError("Unable to establish connection")
            except gaierror:
                raise DataProcessingError("Unable to resolve the URL")
        else:
            raise ValueError("Unsupported slides site")
    else:
        # added this line because when user submits empty url, he wants to unlink prev slide url
        video.slides_source, video.slides_sourceid = u'', u''


@app.route('/<channel>/<playlist>/new', methods=['GET', 'POST'])
@lastuser.requires_login
@load_models(
    (Channel, {'name': 'channel'}, 'channel'),
    (Playlist, {'name': 'playlist', 'channel': 'channel'}, 'playlist'),
    permission='new-video')
def video_new(channel, playlist):
    """
    Add a new video
    """
    form = VideoAddForm()
    if form.validate_on_submit():
        video = Video(playlist=playlist)
        form.populate_obj(video)
        try:
            process_video(video, new=True)
            process_slides(video)
        except (DataProcessingError, ValueError) as e:
            flash(e.message, category="error")
            return render_form(form=form, title=u"New Video", submit=u"Add",
                cancel_url=playlist.url_for(), ajax=False)
        video.make_name()
        playlist.videos.append(video)
        db.session.commit()
        flash(u"Added video '%s'." % video.title, 'success')
        return render_redirect(video.url_for('edit'))
    return render_form(form=form, title=u"New Video", submit=u"Add",
        cancel_url=playlist.url_for(), ajax=False)


# Use /view as a temp workaround to a Werkzeug URLmap sorting bug
@app.route('/<channel>/<playlist>/<video>/view', methods=['GET', 'POST'])
@load_models(
    (Channel, {'name': 'channel'}, 'channel'),
    (Playlist, {'name': 'playlist', 'channel': 'channel'}, 'playlist'),
    (Video, {'url_name': 'video'}, 'video'),
    permission='view')
def video_view(channel, playlist, video):
    """
    View video
    """
    form = VideoActionForm()
    if playlist not in video.playlists:
        # This video isn't in this playlist. Redirect to canonical URL
        return redirect(video.url_for())

    speakers = [plv.playlist.channel for plv in PlaylistVideo.query.filter_by(video=video) if plv.playlist.auto_type == PLAYLIST_AUTO_TYPE.SPEAKING_IN]
    flags = {}
    if g.user:
        starred_playlist = g.user.channel.playlist_for_starred()
        queue_playlist = g.user.channel.playlist_for_queue()
        liked_playlist = g.user.channel.playlist_for_liked()
        disliked_playlist = g.user.channel.playlist_for_disliked()
        flags['starred'] = True if starred_playlist and video in starred_playlist.videos else False
        flags['queued'] = True if queue_playlist and video in queue_playlist.videos else False
        flags['liked'] = True if liked_playlist and video in liked_playlist.videos else False
        flags['disliked'] = True if disliked_playlist and video in disliked_playlist.videos else False
    return render_template('video.html',
        title=video.title, channel=channel, playlist=playlist, video=video,
        form=form, speakers=speakers, flags=flags)


@app.route('/<channel>/<playlist>/<video>/edit', methods=['GET', 'POST'])
@lastuser.requires_login
@load_models(
    (Channel, {'name': 'channel'}, 'channel'),
    (Playlist, {'name': 'playlist', 'channel': 'channel'}, 'playlist'),
    (Video, {'url_name': 'video'}, 'video'),
    permission='edit')
def video_edit(channel, playlist, video):
    """
    Edit video
    """
    if playlist != video.playlist:
        # This video isn't in this playlist. Redirect to canonical URL
        return redirect(video.url_for('edit'))

    form = VideoEditForm(obj=video)
    formvideo = VideoVideoForm(obj=video)
    formslides = VideoSlidesForm(obj=video)
    form_id = request.form.get('form.id')
    if request.method == "POST":
        if form_id == u'video':  # check whether done button is clicked
            if form.validate_on_submit():
                form.populate_obj(video)
                video.make_name()
                db.session.commit()
                flash(u"Edited video '%s'." % video.title, 'success')
                return render_redirect(video.url_for(), code=303)
        elif form_id == u'video_url':  # check video_url was updated
            if formvideo.validate_on_submit():
                formvideo.populate_obj(video)
                process_video(video, new=False)
                db.session.commit()
                return render_redirect(video.url_for('edit'), code=303)
        elif form_id == u'slide_url':  # check slides_url was updated
            if formslides.validate_on_submit():
                formslides.populate_obj(video)
                process_slides(video)
                db.session.commit()
                return render_redirect(video.url_for('edit'), code=303)
    speakers = [plv.playlist.channel for plv in PlaylistVideo.query.filter_by(video=video) if plv.playlist.auto_type == PLAYLIST_AUTO_TYPE.SPEAKING_IN]
    return render_template('videoedit.html',
        channel=channel,
        playlist=playlist,
        video=video,
        form=form,
        formvideo=formvideo,
        formslides=formslides,
        speakers=speakers)


@app.route('/<channel>/<playlist>/<video>/action', methods=['POST'])
@lastuser.requires_login
@load_models(
    (Channel, {'name': 'channel'}, 'channel'),
    (Playlist, {'name': 'playlist', 'channel': 'channel'}, 'playlist'),
    (Video, {'url_name': 'video'}, 'video'),
    permission='edit')
def video_action(channel, playlist, video):
    """
    Perform an action on the video
    """
    form = VideoActionForm()
    if form.validate():
        if form.action.data == 'star':
            pl = g.user.channel.playlist_for_starred(create=True)
            opl = None
            message_added = u"You have starred this video"
            message_removed = u"You have unstarred this video"
        elif form.action.data == 'queue':
            pl = g.user.channel.playlist_for_queue(create=True)
            opl = None
            message_added = u"Added video to watch queue"
            message_removed = u"Removed video from watch queue"
        elif form.action.data == 'like':
            pl = g.user.channel.playlist_for_liked(create=True)
            opl = g.user.channel.playlist_for_disliked()
            message_added = u"You like this video"
            message_removed = u"You have un-liked this video"
        elif form.action.data == 'dislike':
            pl = g.user.channel.playlist_for_disliked(create=True)
            opl = g.user.channel.playlist_for_liked()
            message_added = u"You dislike this video"
            message_removed = u"You have un-disliked this video"
        else:
            return jsonify(message="Unknown action selected",
                           message_type='failure')
        if video in pl.videos:
            pl.videos.remove(video)
            to_return = {'message': message_removed, 'message_type': 'removed'}
        else:
            pl.videos.append(video)
            if opl and video in opl.videos:
                opl.videos.remove(video)
            to_return = {'message': message_added, 'message_type': 'added'}
        db.session.commit()
        return jsonify(to_return)
    elif form.csrf_token.errors:
        return jsonify(message="This page has expired. Please reload and try again",
                       message_type='failure')
    else:
        return jsonify(message="Please select an action to perform on this video",
                       message_type='failure')


@app.route('/<channel>/<playlist>/<video>/add_speaker', methods=['POST'])
@lastuser.requires_login
@load_models(
    (Channel, {'name': 'channel'}, 'channel'),
    (Playlist, {'name': 'playlist', 'channel': 'channel'}, 'playlist'),
    (Video, {'url_name': 'video'}, 'video'),
    permission='edit')
def video_add_speaker(channel, playlist, video):
    """
    Add Speaker to the given video
    """
    form = VideoCsrfForm()
    speaker_name = request.form.get('speaker_name')
    if speaker_name and form.validate():
        # look whether user is present in lastuser, if yes proceed
        userinfo = lastuser.getuser(speaker_name)
        if userinfo:
            speaker_channel = Channel.query.filter_by(userid=userinfo['userid']).first()
            if speaker_channel is None:
                # Create a channel for this speaker. They have never logged in to hasgeek.tv
                # at this point, but when they do, the channel will be waiting for them
                speaker_channel = Channel(userid=userinfo['userid'],
                                          name=userinfo['name'],
                                          title=userinfo['title'],
                                          type=CHANNEL_TYPE.PERSON)
            speaker_playlist = speaker_channel.playlist_for_speaking_in(create=True)
            if video not in speaker_playlist.videos:
                speaker_playlist.videos.append(video)
                to_return = {'message': u"Added %s as speaker" % speaker_channel.title,
                             'message_type': 'added',
                             'userid': speaker_channel.userid,
                             'title': speaker_channel.title}
            else:
                to_return = {'message': u"%s is already tagged as a speaker on this video" % speaker_channel.title,
                             'message_type': 'noop',
                             'userid': speaker_channel.userid,
                             'title': speaker_channel.title}
        else:
            to_return = {'message': 'Could not find a user matching that name or email address',
                         'message_type': 'failure'}
        db.session.commit()
        return jsonify(to_return)
    if form.csrf_token.errors:
        return jsonify(message="This page has expired. Please reload and try again.",
                       message_type='failure')
    abort(400)


@app.route('/<channel>/<playlist>/<video>/remove_speaker', methods=['POST'])
@lastuser.requires_login
@load_models(
    (Channel, {'name': 'channel'}, 'channel'),
    (Playlist, {'name': 'playlist', 'channel': 'channel'}, 'playlist'),
    (Video, {'url_name': 'video'}, 'video'),
    permission='edit')
def video_remove_speaker(channel, playlist, video):
    """
    Delete Speaker to the given video
    """
    form = VideoCsrfForm()
    speaker_userid = request.form.get('speaker_userid')
    if speaker_userid and form.validate():
        speaker_channel = Channel.query.filter_by(userid=speaker_userid).first()
        if speaker_channel:
            speaker_playlist = speaker_channel.playlist_for_speaking_in()
            if speaker_playlist:
                speaker_playlist.videos.remove(video)
                to_return = {'message': u"Removed speaker %s" % speaker_channel.title,
                             'message_type': 'removed',
                             'userid': speaker_channel.userid,
                             'title': speaker_channel.title}
            else:
                to_return = {'message': u"%s is not tagged as speaker for this video" % speaker_channel.title,
                             'message_type': 'failure'}
            db.session.commit()
        else:
            to_return = {'message': u"No such speaker",
                         'message_type': 'failure'}
        return jsonify(to_return)
    if form.csrf_token.errors:
        return jsonify(message="This page has expired. Please reload and try again.",
                       message_type='failure')
    abort(400)


@app.route('/<channel>/<playlist>/<video>/delete', methods=['GET', 'POST'])
@lastuser.requires_login
@load_models(
    (Channel, {'name': 'channel'}, 'channel'),
    (Playlist, {'name': 'playlist', 'channel': 'channel'}, 'playlist'),
    (Video, {'url_name': 'video'}, 'video'),
    permission='delete')
def video_delete(channel, playlist, video):
    """
    Delete video
    """
    if playlist != video.playlist:
        # This video isn't in this playlist. Redirect to canonical URL
        return redirect(video.url_for('delete'))

    return render_delete_sqla(video, db, title=u"Confirm delete",
        message=u"Delete video '%s'? This will remove the video from all playlists it appears in." % video.title,
        success=u"You have deleted video '%s'." % video.title, next=playlist.url_for())


@app.route('/<channel>/<playlist>/<video>/remove', methods=['GET', 'POST'])
@lastuser.requires_login
@load_models(
    (Channel, {'name': 'channel'}, 'channel'),
    (Playlist, {'name': 'playlist', 'channel': 'channel'}, 'playlist'),
    (Video, {'url_name': 'video'}, 'video'),
    permission='remove-video')
def video_remove(channel, playlist, video):
    """
    Remove video from playlist
    """
    if playlist not in video.playlists:
        # This video isn't in this playlist
        abort(404)

    # If this is the primary playlist for this video, refuse to remove it.
    if playlist == video.playlist:
        return render_message(title="Cannot remove",
            message=Markup("Videos cannot be removed from their primary playlist. "
                '<a href="%s">Return to video</a>.' % video.url_for()))

    connection = PlaylistVideo.query.filter_by(playlist_id=playlist.id, video_id=video.id).first_or_404()

    return render_delete_sqla(connection, db, title="Confirm remove",
        message=u"Remove video '%s' from playlist '%s'?" % (video.title, playlist.title),
        success=u"You have removed video '%s' from playlist '%s'." % (video.title, playlist.title),
        next=playlist.url_for())


@app.route('/<channel>/<playlist>/<video>/add', methods=['POST'])
@load_models(
    (Channel, {'name': 'channel'}, 'channel'),
    (Playlist, {'name': 'playlist', 'channel': 'channel'}, 'playlist'),
    (Video, {'url_name': 'video'}, 'video'),
    permission='add-video'
    )
@lastuser.requires_login
def video_playlist_add(channel, playlist, video):
    form = VideoCsrfForm()
    if form.validate_on_submit():
        # CSRF check passed
        if video not in playlist.videos:
            playlist.videos.append(video)
            db.session.commit()
            message = u"Added video to playlist"
            message_type = 'success'
            action = 'add'
        else:
            message = u"This video is already in that playlist"
            message_type = 'info'
            action = 'noop'
    else:
        message = u"CSRF validation failed. Please reload this page and try again."
        message_type = 'error'

    if request.is_xhr:
        return jsonify(message=message, message_type=message_type, action=action, playlist_name=playlist.name)
    else:
        flash(message, message_type)
        if message_type == 'success':
            return redirect(video.url_for('view', channel=channel, playlist=playlist))
        else:
            return redirect(video.url_for('view'))
