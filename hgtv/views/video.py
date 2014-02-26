# -*- coding: utf-8 -*-

import re
import urllib
from urlparse import urlparse, parse_qs
from socket import gaierror
import requests
import bleach
from werkzeug import secure_filename

from flask import render_template, flash, abort, redirect, Markup, request, jsonify, g, json
from coaster.views import load_models
from coaster.gfm import markdown
from baseframe import cache
from baseframe.forms import render_form, render_redirect, render_delete_sqla, render_message, SANITIZE_TAGS, SANITIZE_ATTRIBUTES

from hgtv import app
from hgtv.forms import (VideoAddForm, VideoEditForm, VideoVideoForm, VideoSlidesForm,
                        VideoActionForm, VideoCsrfForm, VideoSlidesSyncForm)
from hgtv.models import db, Channel, Video, Playlist, PlaylistVideo, CHANNEL_TYPE, PLAYLIST_AUTO_TYPE
from hgtv.views.login import lastuser
from hgtv.uploads import thumbnails, return_werkzeug_filestorage


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
                jsondata = r.json() if callable(r.json) else r.json
                if jsondata is None:
                    raise DataProcessingError("Unable to fetch data, please check the youtube url")
                else:
                    if new:
                        video.title = jsondata['entry']['title']['$t']
                        video.description = markdown(jsondata['entry']['media$group']['media$description']['$t'])
                for item in jsondata['entry']['media$group']['media$thumbnail']:
                    if item['yt$name'] == 'mqdefault':
                        thumbnail_url_request = requests.get(item['url'])
                        filestorage = return_werkzeug_filestorage(thumbnail_url_request, filename=secure_filename(jsondata['entry']['title']['$t']))
                        video.thumbnail_path = thumbnails.save(filestorage)
                video.video_sourceid = video_id
                video.video_source = u"youtube"
            except requests.ConnectionError:
                raise DataProcessingError("Unable to establish connection")
            except gaierror:
                raise DataProcessingError("Unable to resolve the hostname")
            except KeyError:
                raise DataProcessingError("Supplied youtube URL doesn't contain video information")
        elif parsed.netloc in ['vimeo.com', 'www.vimeo.com']:
            try:
                components = parsed.path.split('/')
                if len(components) == 2:
                    try:
                        video_id = int(components[-1])
                    except ValueError:
                        raise ValueError("Invalid Video Id. Example: https://vimeo.com/42595773")
                    r = requests.get("https://vimeo.com/api/v2/video/%s.json" % (video_id))
                    jsondata = r.json() if callable(r.json) else r.json
                    if jsondata is None:
                        raise DataProcessingError("Unable to fetch, please check the vimeo url")
                    else:
                        if jsondata[0][u'embed_privacy'] != u'anywhere':
                            raise DataProcessingError("Video is not public to import.")
                        if new:
                            video.title, video.description = jsondata[0]['title'], bleach.clean(jsondata[0]['description'], tags=SANITIZE_TAGS, attributes=SANITIZE_ATTRIBUTES)
                        if jsondata[0]['thumbnail_medium']:
                            thumbnail_url_request = requests.get(jsondata[0]['thumbnail_large'])
                            filestorage = return_werkzeug_filestorage(thumbnail_url_request, filename=secure_filename(jsondata[0]['title']))
                            video.thumbnail_path = thumbnails.save(filestorage)
                    video.video_sourceid, video.video_source, video.video_url = video_id, u"vimeo", jsondata[0]['url']
                else:
                    raise DataProcessingError("Invalid Vimeo url. Example: https://vimeo.com/42595773")
            except requests.ConnectionError:
                raise DataProcessingError("Unable to establish connection")
            except gaierror:
                raise DataProcessingError("Unable to resolve the hostname")
            except KeyError:
                raise DataProcessingError("")
        elif parsed.netloc in ["ustream.tv", "www.ustream.tv"]:
            try:
                components = [item for item in parsed.path.split("/") if item != ""]
                if len(components) == 2:
                    try:
                        video_id = int(components[-1])
                    except ValueError:
                        raise ValueError("Invalid Ustream Id. Example: https://www.ustream.tv/channel/6320346")
                    try:
                        r = requests.get("https://api.ustream.tv/json/channel/%s/getInfo" % (components[1]), params={"key": app.config['USTREAM_KEY']})
                    except KeyError:
                        raise DataProcessingError("Ustream Developer key is missing")
                    jsondata = r.json() if callable(r.json) else r.json
                    if jsondata is None:
                        raise DataProcessingError("Unable to fetch, please check the ustream url")
                    else:
                        if new:
                            video.title, video.description = jsondata['results']['title'], markdown(jsondata['results']['description']) or ""
                        if jsondata['results']['imageUrl']:
                            thumbnail_url_request = requests.get(jsondata['results']['imageUrl']['medium'])
                            filestorage = return_werkzeug_filestorage(thumbnail_url_request, filename=secure_filename(jsondata['results']['title']))
                            video.thumbnail_path = thumbnails.save(filestorage)
                    video.video_sourceid, video.video_source = video_id, u"ustream"
                else:
                    raise DataProcessingError("Invalid ustream url. Example: https://www.ustream.tv/channel/6320346")
            except requests.ConnectionError:
                raise DataProcessingError("Unable to establish connection")
            except gaierror:
                raise DataProcessingError("Unable to resolve the hostname")
            except KeyError as e:
                raise DataProcessingError(e)
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
                r = requests.get('https://www.slideshare.net/api/oembed/2?url=%s&format=json' % video.slides_url)
                jsondata = r.json() if callable(r.json) else r.json
                if jsondata:
                    video.slides_source = u'slideshare'
                    video.slides_sourceid = jsondata['slideshow_id']
                else:
                    raise DataProcessingError("Unable to fetch data, please check the slideshare url")
            except requests.ConnectionError:
                raise DataProcessingError("Unable to establish connection")
            except gaierror:
                raise DataProcessingError("Unable to resolve the URL")
        elif parsed.netloc in ['speakerdeck.com', 'www.speakerdeck.com']:
            try:
                r = requests.get('https://speakerdeck.com/oembed.json?url=%s' % video.slides_url)
                jsondata = r.json() if callable(r.json) else r.json
                if jsondata:
                    video.slides_source = u'speakerdeck'
                    pattern = u'\Wsrc="//speakerdeck.com/player/([^\s^"]+)'  # pattern to extract slideid from speakerdeck
                    video.slides_sourceid = re.findall(pattern, jsondata['html'])[0]
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


def get_slideshare_unique_value(url):
    r = requests.get('https://www.slideshare.net/api/oembed/2?url=%s&format=json' % urllib.quote(url))
    jsondata = r.json() if callable(r.json) else r.json
    return jsondata['slide_image_baseurl'].split('/')[-3]


def make_presentz_json(video, json_value):
    if video.video_source == "youtube":
        d = {"chapters": [{"video": {"url": "https://www.youtube.com/watch?v=" + video.video_sourceid, }}]}
    elif video.video_source == "vimeo":
        d = {"chapters": [{"video": {"url": video.video_url, }}]}
    if video.slides_source == u'slideshare':
        unique_value = get_slideshare_unique_value(video.slides_url)
        d['chapters'][0]['slides'] = [{'time': str(key), "public_url": urllib.quote(video.slides_url), "url": 'https://slideshare.net/' + unique_value + "#" + str(val)} for key, val in json_value.items()]
    elif video.slides_source == u'speakerdeck':
        #json to supply for presentz syncing
        d['chapters'][0]['slides'] = [{'time': str(key), "url": 'https://speakerdeck.com/' + urllib.quote(video.slides_sourceid) + "#" + str(val)} for key, val in json_value.items()]
    return json.dumps(d)


def add_new_video(channel, playlist):
    form = VideoAddForm()
    if form.validate_on_submit():
        stream_playlist = channel.playlist_for_stream(create=True)
        video = Video(playlist=playlist if playlist is not None else stream_playlist)
        form.populate_obj(video)
        try:
            process_video(video, new=True)
            process_slides(video)
        except (DataProcessingError, ValueError) as e:
            flash(e.message, category="error")
            return render_form(form=form, title=u"New Video", submit=u"Add",
                               cancel_url=channel.url_for(), ajax=False)
        video.make_name()
        if playlist is not None and video not in playlist.videos:
            playlist.videos.append(video)
        if video not in stream_playlist.videos:
            stream_playlist.videos.append(video)
        db.session.commit()
        flash(u"Added video '%s'." % video.title, 'success')
        return render_redirect(video.url_for('edit'))
    if playlist is None:
        cancel_url = channel.url_for()
    else:
        cancel_url = playlist.url_for()
    return render_form(form=form, title=u"New Video", submit=u"Add",
                       cancel_url=cancel_url, ajax=False)


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
    return add_new_video(channel, playlist)


# Because of a Werkzeug routing bug, three-part routes like /<channel>/<playlist>/<video>
# get higher ranking than /static/<path:filename>, making it impossible to access static
# resources. We therefore use a simple catch-all path and parse the URL and find the models
# ourselves, skipping load_models here.
@app.route('/<path:videopath>', methods=['GET', 'POST'])
def video_view(videopath):
    """
    View video
    """
    pathparts = videopath.split('/')
    if not pathparts[0]:  # Did we somehow get a /-prefixed path?
        pathparts.pop(0)
    try:
        channel_name, playlist_name, video_name = pathparts[:3]
    except ValueError:
        # Got something that isn't three parts?
        abort(404)
    channel = Channel.query.filter_by(name=channel_name).first()  # Not first_or_404
    playlist = Playlist.query.filter_by(name=playlist_name, channel=channel).first()  # No 404
    try:
        video_id = int(video_name.split('-')[0])
    except ValueError:
        abort(404)
    video = Video.query.get(video_id)
    if video is None:
        abort(404)
    if channel is None or playlist not in video.playlists:
        # This video isn't in this playlist. Redirect to canonical URL
        return redirect(video.url_for())
    if video.url_name != video_name:
        # This video's URL has changed
        return redirect(video.url_for('view', channel=channel, playlist=playlist))

    g.permissions = video.permissions(g.user)

    form = VideoActionForm()
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
    formsync = VideoSlidesSyncForm(obj=video)
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
                try:
                    process_video(video, new=False)
                except (DataProcessingError, ValueError) as e:
                    flash(e.message, category="error")
                db.session.commit()
                return render_redirect(video.url_for('edit'), code=303)
        elif form_id == u'slide_url':  # check slides_url was updated
            if formslides.validate_on_submit():
                formslides.populate_obj(video)
                try:
                    process_slides(video)
                    if video.video_slides_mapping:
                        video.video_slides_mapping_json = make_presentz_json(video, json.loads(video.video_slides_mapping))
                except (DataProcessingError, ValueError) as e:
                    flash(e.message, category="error")
                db.session.commit()
                return render_redirect(video.url_for('edit'), code=303)
        elif form_id == u'video_slides_sync':
            if formsync.validate_on_submit():
                formsync.populate_obj(video)
                try:
                    if video.video_slides_mapping:
                        video.video_slides_mapping_json = make_presentz_json(video, json.loads(video.video_slides_mapping))
                    else:
                        flash(u"No value found for syncing video and slides", "error")
                except ValueError:
                    flash(u"SyntaxError in video slides mapping value", "error")
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
        formsync=formsync,
        speakers=speakers,
        autocomplete_url=lastuser.endpoint_url(lastuser.getuser_autocomplete_endpoint),
        slideshare_unique_value=get_slideshare_unique_value(video.slides_url) if video.slides_source == u'slideshare' else None)


@app.route('/<channel>/<playlist>/<video>/action', methods=['POST'])
@lastuser.requires_login
@load_models(
    (Channel, {'name': 'channel'}, 'channel'),
    (Playlist, {'name': 'playlist', 'channel': 'channel'}, 'playlist'),
    (Video, {'url_name': 'video'}, 'video'),
    permission='view')
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
    speaker_buid = request.form.get('speaker_name')
    if speaker_buid and form.validate():
        # look whether user is present in lastuser, if yes proceed
        userinfo = lastuser.getuser_by_userid(speaker_buid)
        if userinfo:
            speaker_channel = Channel.query.filter_by(userid=userinfo['userid']).first()
            if speaker_channel is None:
                # Create a channel for this speaker. They have never logged in to hasgeek.tv
                # at this point, but when they do, the channel will be waiting for them
                speaker_channel = Channel(userid=userinfo['userid'],
                                          name=userinfo['name'] or userinfo['userid'],
                                          title=userinfo['title'],
                                          type=CHANNEL_TYPE.PERSON)
                db.session.add(speaker_channel)
            else:
                speaker_channel.title = userinfo['title']
                speaker_channel.name = userinfo['name'] or userinfo['userid']
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
            cache.delete('data/featured-channels')
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
