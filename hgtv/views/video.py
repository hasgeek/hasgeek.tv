# -*- coding: utf-8 -*-

import re
import urllib
from urlparse import urlparse, parse_qs
from socket import gaierror
import requests
import urllib2
import bleach
from werkzeug import secure_filename

from flask import abort, redirect, request, jsonify, g, json, url_for, make_response
from coaster.views import load_models, render_with
from coaster.gfm import markdown
from baseframe import cache, _
from baseframe.forms import render_form, SANITIZE_TAGS, SANITIZE_ATTRIBUTES

from hgtv import app
from hgtv.forms import VideoAddForm, VideoEditForm, VideoActionForm, VideoCsrfForm
from hgtv.models import db, Channel, Video, Playlist, PlaylistVideo, CHANNEL_TYPE, PLAYLIST_AUTO_TYPE
from hgtv.views.login import lastuser
from hgtv.uploads import thumbnails, return_werkzeug_filestorage
from hgtv.services.channel_details import get_channel_details
from hgtv.services.playlist_details import get_playlist_details
from hgtv.services.video_details import get_video_details, get_embed_video_details, get_video_action_permissions, get_user_preference
from hgtv.services.related_video_details import get_related_video_details
from hgtv.services.speaker_details import get_speaker_details


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
                r = requests.get('https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&key={api_key}'.format(
                    video_id=video_id, api_key=app.config['YOUTUBE_API_KEY']
                ))
                try:
                    jsondata = r.json()
                except ValueError as e:
                    app.logger.error("Error while fetching video details\n\nError: {error}\nResponse body: {response}".format(
                        error=e.message, response=r.text))
                    raise DataProcessingError("Unable to parse video data, please try after sometime")
                if jsondata is None or len(jsondata['items']) == 0:
                    raise DataProcessingError("Unable to fetch data, please check the youtube url")
                else:
                    jsondata = jsondata['items'][0]
                    if new:
                        video.title = jsondata['snippet']['title']
                        video.description = markdown(jsondata['snippet']['description'])
                    thumbnail_url_request = requests.get(jsondata['snippet']['thumbnails']['medium']['url'])
                    filestorage = return_werkzeug_filestorage(thumbnail_url_request, filename=secure_filename(video.title))
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
                    jsondata = r.json()
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
                    jsondata = r.json()
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
                jsondata = r.json()
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
                r = urllib2.urlopen('https://speakerdeck.com/oembed.json?url=%s' % video.slides_url)
                jsondata = json.loads(r.read())
                r.close()
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
    jsondata = r.json()
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
        # json to supply for presentz syncing
        d['chapters'][0]['slides'] = [{'time': str(key), "url": 'https://speakerdeck.com/' + urllib.quote(video.slides_sourceid) + "#" + str(val)} for key, val in json_value.items()]
    return json.dumps(d)


def add_new_video(data):
    playlist = data['playlist']
    channel = data['channel']
    form = VideoAddForm()
    if request.method == 'GET':
        if playlist is None:
            cancel_url = channel.url_for()
        else:
            cancel_url = playlist.url_for()
        html_form = render_form(form=form, title=u"New Video", submit=u"Add",
                           cancel_url=cancel_url, ajax=False, with_chrome=False)
        return jsonify(channel=get_channel_details(channel),
            playlist=get_playlist_details(channel, playlist, videos_count='none') if playlist else '',
            form=html_form)
    if form.validate_on_submit():
        stream_playlist = channel.playlist_for_stream(create=True)
        video = Video(playlist=playlist if playlist is not None else stream_playlist)
        form.populate_obj(video)
        try:
            process_video(video, new=True)
            process_slides(video)
        except (DataProcessingError, ValueError) as e:
            return make_response(jsonify(status='error', errors={'error': [e.message]}), 400)
        video.make_name()
        if playlist is not None and video not in playlist.videos:
            playlist.videos.append(video)
        if video not in stream_playlist.videos:
            stream_playlist.videos.append(video)
        db.session.commit()
        return make_response(jsonify(status='ok', doc=_(u"Added video {title}.".format(title=video.title)), result={'new_video_edit_url': video.url_for('edit')}), 201)
    else:
        return make_response(jsonify(status='error', errors=form.errors), 400)


@app.route('/<channel>/<playlist>/new', methods=['GET', 'POST'])
@lastuser.requires_login
@render_with({'text/html': 'index.html.jinja2', 'application/json': add_new_video})
@load_models(
    (Channel, {'name': 'channel'}, 'channel'),
    (Playlist, {'name': 'playlist', 'channel': 'channel'}, 'playlist'),
    permission='new-video')
def video_new(channel, playlist):
    """
    Add a new video
    """
    return dict(channel=channel, playlist=playlist)


def jsonify_video_view(data):
    channel_dict = get_channel_details(data['channel'])
    playlist_dict = get_playlist_details(data['channel'], data['playlist'], 'none')
    video_dict = get_embed_video_details(data['channel'], data['playlist'], data['video'])
    video_dict.update(get_video_action_permissions(data['channel'], data['playlist'], data['video']))
    speakers_dict = [get_speaker_details(speaker) for speaker in data['speakers']]
    related_videos_dict = get_related_video_details(data['channel'], data['playlist'], data['video'])
    return jsonify(channel=channel_dict, playlist=playlist_dict, video=video_dict,
        speakers=speakers_dict, relatedVideos=related_videos_dict, user=data['user'])


# Because of a Werkzeug routing bug, three-part routes like /<channel>/<playlist>/<video>
# get higher ranking than /static/<path:filename>, making it impossible to access static
# resources. We therefore use a simple catch-all path and parse the URL and find the models
# ourselves, skipping load_models here.
@app.route('/<path:videopath>', methods=['GET', 'POST'])
@render_with({'text/html': 'index.html.jinja2', 'application/json': jsonify_video_view})
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

    speakers = [plv.playlist.channel for plv in PlaylistVideo.query.filter_by(video=video) if plv.playlist.auto_type == PLAYLIST_AUTO_TYPE.SPEAKING_IN]
    g.permissions = video.permissions(g.user)
    user = {}
    user['flags'] = {}
    if g.user:
        user['logged_in'] = True
        user['flags'] = get_user_preference(g.user, video)
    else:
        user['logged_in'] = False
        user['login_url'] = url_for('login')

    return dict(channel=channel, playlist=playlist,
        video=video, speakers=speakers, user=user)


def handle_edit_video(data):
    playlist = data['playlist']
    channel = data['channel']
    video = data['video']
    current_speakers = [speaker.userid for speaker in video.speakers]
    form = VideoEditForm(obj=video)
    if request.method == 'GET':
        html_form = render_form(form=form, title="Edit Video", submit=u"Save",
            cancel_url=video.url_for(), ajax=False, with_chrome=False)
        return jsonify(video=get_video_details(channel, playlist, video), form=html_form)
    if form.validate():
        form.populate_obj(video)
        if not playlist.name:
            video.make_name()
        if video.video_url != form.video_url.data:
            try:
                process_video(video, new=False)
            except (DataProcessingError, ValueError) as e:
                return make_response(jsonify(status='error', errors={'error': [e.message]}), 400)
        if video.slides_url != form.slides_url.data:
            try:
                process_slides(video)
                if video.video_slides_mapping:
                    video.video_slides_mapping_json = make_presentz_json(video, json.loads(video.video_slides_mapping))
            except (DataProcessingError, ValueError) as e:
                return make_response(jsonify(status='error', errors={'error': [e.message]}), 400)
        new_speakers = [new_speaker.userid for new_speaker in form.speakers.data]
        for current_speaker in current_speakers:
            # Remove speaker
            if current_speaker not in new_speakers:
                speaker_channel = Channel.query.filter_by(userid=current_speaker).first()
                if speaker_channel:
                    speaker_playlist = speaker_channel.playlist_for_speaking_in()
                    if speaker_playlist:
                        speaker_playlist.videos.remove(video)
        for new_speaker in new_speakers:
            # Add speaker
            if new_speaker not in current_speakers:
                userinfo = lastuser.getuser_by_userid(new_speaker)
                if userinfo:
                    speaker_channel = Channel.query.filter_by(userid=new_speaker).first()
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
                else:
                    return make_response(jsonify(status='error', errors=['Could not find a user matching that name or email address']), 400)
        db.session.commit()
        return make_response(jsonify(status='ok', doc=_(u"Edited video {title}.".format(title=video.title)), result={}), 201)
    return make_response(jsonify(status='error', errors=form.errors), 400)


@app.route('/<channel>/<playlist>/<video>/edit', methods=['GET', 'POST'])
@lastuser.requires_login
@render_with({'text/html': 'index.html.jinja2', 'application/json': handle_edit_video})
@load_models(
    (Channel, {'name': 'channel'}, 'channel'),
    (Playlist, {'name': 'playlist', 'channel': 'channel'}, 'playlist'),
    (Video, {'url_name': 'video'}, 'video'),
    permission='edit')
def video_edit(channel, playlist, video):
    """
    Edit video
    """
    return dict(channel=channel, playlist=playlist, video=video)


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
            return make_response(jsonify(status='error', errors={'error': ["Unknown action selected"]}), 400)
        if video in pl.videos:
            pl.videos.remove(video)
            to_return = {'message': message_removed, 'message_type': 'removed'}
        else:
            pl.videos.append(video)
            if opl and video in opl.videos:
                opl.videos.remove(video)
            to_return = {'message': message_added, 'message_type': 'added'}
        db.session.commit()
        return make_response(jsonify(status='ok', doc=to_return['message'], result={'flags': get_user_preference(g.user, video)}), 200)
    elif form.csrf_token.errors:
        return make_response(jsonify(status='error', errors={'error': ["This page has expired. Please reload and try again"]}), 400)
    else:
        return make_response(jsonify(status='error', errors={'error': ["Please select an action to perform on this video"]}), 400)


def handle_delete_video(data):
    playlist = data['playlist']
    channel = data['channel']
    video = data['video']
    if request.method == 'GET':
        return jsonify(video=get_video_details(channel, playlist, video))
    form = VideoCsrfForm()
    if form.validate_on_submit():
        db.session.delete(video)
        db.session.commit()
        return make_response(jsonify(status='ok', doc=_(u"Delete video {title}.".format(title=video.title)), result={}), 200)
    return make_response(jsonify(status='error', errors={'error': form.errors}), 400)


@app.route('/<channel>/<playlist>/<video>/delete', methods=['GET', 'POST'])
@lastuser.requires_login
@load_models(
    (Channel, {'name': 'channel'}, 'channel'),
    (Playlist, {'name': 'playlist', 'channel': 'channel'}, 'playlist'),
    (Video, {'url_name': 'video'}, 'video'),
    permission='delete')
@render_with({'text/html': 'index.html.jinja2', 'application/json': handle_delete_video})
def video_delete(channel, playlist, video):
    """
    Delete video
    """
    return dict(channel=channel, playlist=playlist, video=video)


def handle_remove_video(data):
    playlist = data['playlist']
    channel = data['channel']
    video = data['video']
    if request.method == 'GET':
        return jsonify(playlist=get_playlist_details(channel, playlist, videos_count='none'),
            video=get_video_details(channel, playlist, video))
    if playlist not in video.playlists:
        return make_response(jsonify(status='error', errors={'error': ['Video not playlist and cannot be removed']}), 400)

    # If this is the primary playlist for this video, refuse to remove it.
    if playlist == video.playlist:
        return make_response(jsonify(status='error', errors={'error': ['Videos cannot be removed from their primary playlist']}), 400)
    form = VideoCsrfForm()
    if form.validate_on_submit():
        connection = PlaylistVideo.query.filter_by(playlist_id=playlist.id, video_id=video.id).first_or_404()
        db.session.delete(connection)
        db.session.commit()
        return make_response(jsonify(status='ok', doc=_(u"Remove video {video} from {playlist}.".format(video=video.title, playlist=playlist.title)), result={}), 200)
    return make_response(jsonify(status='error', errors={'error': form.errors}), 400)


@app.route('/<channel>/<playlist>/<video>/remove', methods=['GET', 'POST'])
@lastuser.requires_login
@load_models(
    (Channel, {'name': 'channel'}, 'channel'),
    (Playlist, {'name': 'playlist', 'channel': 'channel'}, 'playlist'),
    (Video, {'url_name': 'video'}, 'video'),
    permission='remove-video')
@render_with({'text/html': 'index.html.jinja2', 'application/json': handle_remove_video})
def video_remove(channel, playlist, video):
    """
    Remove video from playlist
    """
    return dict(channel=channel, playlist=playlist, video=video)


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
        if video not in playlist.videos:
            playlist.videos.append(video)
            db.session.commit()
            cache.delete('data/featured-channels')
            message = u"Added video to playlist"
        else:
            message = u"This video is already in that playlist"
        return make_response(jsonify(status='ok', doc=message, result={'url': playlist.url_for()}), 200)
    else:
        message = u"CSRF validation failed. Please reload this page and try again."
        return make_response(jsonify(status='error', errors={'error': [message]}), 400)
