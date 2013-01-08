# -*- coding: utf-8 -*-

from urlparse import urlparse, parse_qs
from socket import gaierror
import requests
from werkzeug import secure_filename

from flask import render_template, flash, escape, request, jsonify
from coaster.views import load_model, load_models
from baseframe.forms import render_redirect, render_form, render_delete_sqla
from hgtv import app
from hgtv.views.login import lastuser
from hgtv.forms import PlaylistForm, PlaylistImportForm
from hgtv.models import db, Channel, Playlist, Video
from hgtv.views.video import DataProcessingError
from hgtv.uploads import thumbnails, return_werkzeug_filestorage


#helpers
def process_playlist(playlist, playlist_url, channel):
    """
    Get metadata for the playlist from the corresponding site
    """
    # Parse the playlist url
    if playlist_url:
        parsed = urlparse(escape(playlist_url))
        # Check video source and get corresponding data
        if parsed.netloc in ['youtube.com', 'www.youtube.com']:
            try:
                # first two character of playlist id says what type of playlist, ignore them
                playlist_id = parse_qs(parsed.query)['list'][0][2:]

                def inner(start_index=1, max_result=50, total=0):
                    """Retireves youtube playlist videos recursively

                    :param start_index: Index to start for fetching videos in playlist
                    :param max_result: Maximum results to return
                    :param total: variable to keep track of total videos fetched
                    """
                    r = requests.get('http://gdata.youtube.com/feeds/api/playlists/%s?v=2&alt=json&max-result=50&start-index=%d' % (playlist_id, start_index))
                    jsondata = r.json() if callable(r.json) else r.json
                    if jsondata is None:
                        raise DataProcessingError("Unable to fetch data, please check the youtube url")
                    else:
                        # fetch playlist info
                        # prevent overwriting title during Extend playlist
                        playlist.title = playlist.title or jsondata['feed']['title']['$t']
                        if 'media$description' in jsondata['feed']['media$group']:
                            playlist.description = escape(jsondata['feed']['media$group']['media$description']['$t'])
                        for item in jsondata['feed'].get('entry', []):
                            if item.get('app$control', {}).get('yt$state', {}).get('reasonCode'):  # Is it private?
                                continue
                            videos = Video.query.filter_by(video_source=u"youtube", video_sourceid=item['media$group']['yt$videoid']['$t']).all()
                            if videos:
                                # If video isn't present in current playlist, copy the video parameters
                                if not filter(lambda video: video.playlist == playlist, videos):
                                    new_video = Video(playlist=playlist)
                                    video = videos[0]
                                    new_video.name = video.name
                                    new_video.title = video.title
                                    new_video.video_url = video.video_url
                                    new_video.description = video.description
                                    new_video.thumbnail_path = video.thumbnail_path
                                    new_video.video_source = u"youtube"
                                    new_video.video_sourceid = video.video_sourceid
                                    playlist.videos.append(new_video)
                                    stream_playlist = channel.playlist_for_stream(create=True)
                                    stream_playlist.videos.append(new_video)
                            else:
                                video = Video(playlist=playlist)
                                video.title = item['title']['$t']
                                video.video_url = item['media$group']['media$player']['url']
                                if 'media$description' in item['media$group']:
                                    video.description = escape(item['media$group']['media$description']['$t'])
                                for video_content in item['media$group']['media$thumbnail']:
                                    if video_content['yt$name'] == 'mqdefault':
                                        thumbnail_url_request = requests.get(video_content['url'])
                                        filestorage = return_werkzeug_filestorage(thumbnail_url_request,
                                            filename=secure_filename(item['title']['$t']) or 'name-missing')
                                        video.thumbnail_path = thumbnails.save(filestorage)
                                video.video_sourceid = item['media$group']['yt$videoid']['$t']
                                video.video_source = u"youtube"
                                video.make_name()
                                playlist.videos.append(video)
                                stream_playlist = channel.playlist_for_stream(create=True)
                                stream_playlist.videos.append(video)
                        #When no more data is present to retrieve in playlist 'feed' is absent in json
                        if 'entry' in jsondata['feed']:
                            total += len(jsondata['feed']['entry'])
                            if total <= jsondata['feed']['openSearch$totalResults']:
                                # check for empty playlist
                                if not jsondata['feed'].get('entry', []):
                                    raise DataProcessingError("Empty Playlist")
                                inner(start_index=total + 1, total=total)
                inner()
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


@app.route('/<channel>/new', methods=['GET', 'POST'])
@lastuser.requires_login
@load_model(Channel, {'name': 'channel'}, 'channel', permission='new-playlist')
def playlist_new(channel):
    # Make a new playlist
    form = PlaylistForm()
    form.channel = channel
    if form.validate_on_submit():
        playlist = Playlist(channel=channel)
        form.populate_obj(playlist)
        if not playlist.name:
            playlist.make_name()
        db.session.add(playlist)
        db.session.commit()
        flash(u"Created playlist '%s'." % playlist.title, 'success')
        return render_redirect(playlist.url_for(), code=303)
    return render_form(form=form, title="New Playlist", submit=u"Create",
        cancel_url=channel.url_for(), ajax=True)


@app.route('/<channel>/<playlist>/edit', methods=['GET', 'POST'])
@lastuser.requires_login
@load_models(
    (Channel, {'name': 'channel'}, 'channel'),
    (Playlist, {'name': 'playlist', 'channel': 'channel'}, 'playlist'),
    permission='edit')
def playlist_edit(channel, playlist):
    form = PlaylistForm(obj=playlist)
    form.channel = channel
    if form.validate_on_submit():
        form.populate_obj(playlist)
        db.session.commit()
        flash(u"Edited playlist '%s'" % playlist.title, 'success')
        return render_redirect(playlist.url_for(), code=303)
    return render_form(form=form, title="Edit Playlist", submit=u"Save",
        cancel_url=playlist.url_for(), ajax=True)


@app.route('/<channel>/<playlist>/delete', methods=['GET', 'POST'])
@lastuser.requires_login
@load_models(
    (Channel, {'name': 'channel'}, 'channel'),
    (Playlist, {'name': 'playlist', 'channel': 'channel'}, 'playlist'),
    permission='delete'
    )
def playlist_delete(channel, playlist):
    return render_delete_sqla(playlist, db, title=u"Confirm delete",
        message=u"Delete playlist '%s'? This cannot be undone." % playlist.title,
        success=u"You have deleted playlist '%s'." % playlist.title,
        next=channel.url_for())


@app.route('/<channel>/<playlist>')
@load_models(
    (Channel, {'name': 'channel'}, 'channel'),
    (Playlist, {'name': 'playlist', 'channel': 'channel'}, 'playlist'),
    permission='view')
def playlist_view(channel, playlist):
    return render_template('playlist.html', channel=channel, playlist=playlist)


@app.route('/<channel>/import', methods=['GET', 'POST'])
@lastuser.requires_login
@load_model(Channel, {'name': 'channel'}, 'channel', permission='new-playlist')
def playlist_import(channel):
    # Import playlist
    form = PlaylistImportForm()
    form.channel = channel
    if form.validate_on_submit():
        playlist = Playlist(channel=channel)
        form.populate_obj(playlist)
        try:
            process_playlist(playlist, playlist_url=form.playlist_url.data, channel=channel)
            if not playlist.name:
                playlist.make_name()
            db.session.add(playlist)
            db.session.commit()
        except (DataProcessingError, ValueError) as e:
            flash(e.message, category="error")
            return render_form(form=form, title="Import Playlist", submit=u"Import",
                cancel_url=channel.url_for(), ajax=False)
        flash(u"Imported playlist '%s'." % playlist.title, 'success')
        return render_redirect(playlist.url_for(), code=303)
    return render_form(form=form, title="Import Playlist", submit=u"Import",
        cancel_url=channel.url_for(), ajax=False)


@app.route('/<channel>/<playlist>/extend', methods=['GET', 'POST'])
@lastuser.requires_login
@load_models(
    (Channel, {'name': 'channel'}, 'channel'),
    (Playlist, {'name': 'playlist', 'channel': 'channel'}, 'playlist'),
    permission='extend')
def playlist_extend(channel, playlist):
    form = PlaylistImportForm()
    form.channel = channel
    html = render_template('playlist-extend.html', form=form, channel=channel, playlist=playlist)
    if request.is_xhr:
        if form.validate_on_submit():
            playlist_url = escape(form.playlist_url.data)
            initial_count = len(playlist.videos)
            try:
                process_playlist(playlist_url=playlist_url, playlist=playlist, channel=channel)
            except:
                return jsonify({'message_type': "server-error",
                    'message': 'Oops, something went wrong, please try later'})
            additions = (len(playlist.videos) - initial_count)
            if additions:
                db.session.commit()
                flash(u"Added '%d' videos" % (len(playlist.videos) - initial_count), 'success')
                return jsonify({'message_type': "success", 'action': 'redirect', 'url': playlist.url_for()})
            return jsonify({'message_type': "success", 'action': 'noop', 'message': 'Already upto date'})
        if form.errors:
            html = render_template('playlist-extend.html', form=form, channel=channel, playlist=playlist)
            return jsonify({'message_type': "error", 'action': 'append',
                'html': html})
        return jsonify({'action': 'modal-window', 'message_type': 'success', 'html': html})
    return html
