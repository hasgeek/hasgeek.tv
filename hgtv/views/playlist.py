import os
from datetime import date
from socket import gaierror
from urllib.parse import parse_qs, urlparse

import requests
from apiclient.discovery import build
from apiclient.errors import HttpError
from flask import Response, escape, render_template, request, url_for
from werkzeug.utils import secure_filename

from baseframe import _, cache
from baseframe.forms import Form, render_form
from coaster.gfm import markdown
from coaster.utils import utcnow
from coaster.views import load_model, load_models, render_with

from hgtv import app
from hgtv.forms import PlaylistForm, PlaylistImportForm
from hgtv.models import Channel, Playlist, PlaylistRedirect, Video, db
from hgtv.uploads import UploadNotAllowed, return_werkzeug_filestorage, thumbnails
from hgtv.views.login import lastuser
from hgtv.views.video import DataProcessingError


# helpers
def process_playlist(playlist, playlist_url):
    """
    Get metadata for the playlist from the corresponding site
    """
    # Parse the playlist url
    if playlist_url:
        parsed = urlparse(escape(playlist_url))
        # Check video source and get corresponding data
        if parsed.netloc in ['youtube.com', 'www.youtube.com']:
            try:
                stream_playlist = playlist.channel.playlist_for_stream(create=True)
                # first two character of playlist id says what type of playlist, ignore them
                playlist_id = parse_qs(parsed.query)['list'][0][2:]
                youtube = build(
                    'youtube', 'v3', developerKey=app.config['YOUTUBE_API_KEY']
                )
                playlistitems_list_request = youtube.playlistItems().list(
                    playlistId=playlist_id, part='snippet', maxResults=50
                )
                playlist_info_request = youtube.playlists().list(
                    id=playlist_id, part='snippet'
                )
                if playlist_info_request:
                    playlist_infos = playlist_info_request.execute()
                    for playlist_info in playlist_infos['items']:
                        playlist.title = (
                            playlist.title or playlist_info['snippet']['title']
                        )
                        if playlist_info['snippet']['description']:
                            playlist.description = playlist_info['snippet'][
                                'description'
                            ]
                while playlistitems_list_request:
                    playlistitems_list_response = playlistitems_list_request.execute()
                    for playlist_item in playlistitems_list_response['items']:
                        with db.session.no_autoflush:
                            video = Video.query.filter_by(
                                video_source='youtube',
                                channel=playlist.channel,
                                video_sourceid=playlist_item['snippet']['resourceId'][
                                    'videoId'
                                ],
                            ).first()
                        if video:
                            if video not in stream_playlist.videos:
                                stream_playlist.videos.append(video)
                            if video not in playlist.videos:
                                playlist.videos.append(video)
                        else:
                            video = Video(
                                playlist=(
                                    playlist
                                    if playlist is not None
                                    else stream_playlist
                                )
                            )
                            video.title = playlist_item['snippet']['title']
                            video.video_url = (
                                'https://www.youtube.com/watch?v='
                                + playlist_item['snippet']['resourceId']['videoId']
                            )
                            if playlist_item['snippet']['description']:
                                video.description = markdown(
                                    playlist_item['snippet']['description']
                                )
                            for thumbnail in playlist_item['snippet']['thumbnails'][
                                'medium'
                            ]:
                                thumbnail_url_request = requests.get(
                                    playlist_item['snippet']['thumbnails']['medium'][
                                        'url'
                                    ]
                                )
                                filestorage = return_werkzeug_filestorage(
                                    thumbnail_url_request,
                                    filename=secure_filename(
                                        playlist_item['snippet']['title']
                                    )
                                    or 'name-missing',
                                )
                                video.thumbnail_path = thumbnails.save(filestorage)
                            video.video_sourceid = playlist_item['snippet'][
                                'resourceId'
                            ]['videoId']
                            video.video_source = 'youtube'
                            video.make_name()
                            playlist.videos.append(video)
                            with db.session.no_autoflush:
                                if video not in stream_playlist.videos:
                                    stream_playlist.videos.append(video)
                    playlistitems_list_request = youtube.playlistItems().list_next(
                        playlistitems_list_request, playlistitems_list_response
                    )
            except requests.ConnectionError:
                raise DataProcessingError("Unable to establish connection")
            except gaierror:
                raise DataProcessingError("Unable to resolve the hostname")
            except KeyError:
                raise DataProcessingError(
                    "Supplied youtube URL doesn't contain video information"
                )
            except HttpError:
                raise DataProcessingError("HTTPError while parsing YouTube playlist")
        else:
            raise ValueError("Unsupported video site")
    else:
        raise ValueError("Video URL is missing")


def remove_banner_ad(filename):
    try:
        os.remove(os.path.join(app.static_folder, 'thumbnails', filename))
    except OSError:
        pass


@app.route('/<channel>/new', methods=['GET', 'POST'])
@lastuser.requires_login
@render_with({'text/html': 'index.html.jinja2'}, json=True)
@load_model(Channel, {'name': 'channel'}, 'channel', permission='new-playlist')
def playlist_new(channel):
    form = PlaylistForm()
    form.channel = channel
    if request.method == 'GET':
        form.published_date.data = date.today()
        html_form = render_form(
            form=form,
            title=_("New Playlist"),
            submit=_("Create"),
            cancel_url=channel.url_for(),
            ajax=True,
            with_chrome=False,
        ).get_data(as_text=True)
        return {'channel': dict(channel.current_access()), 'form': html_form}
    try:
        if form.validate_on_submit():
            playlist = Playlist(channel=channel)
            form.populate_obj(playlist)
            if not playlist.name:
                playlist.make_name()
            db.session.add(playlist)
            db.session.commit()
            return {
                'status': 'ok',
                'doc': _("Created playlist {title}.").format(title=playlist.title),
                'result': {'new_playlist_url': playlist.url_for()},
            }, 201
        return {'status': 'error', 'errors': form.errors}, 400
    except UploadNotAllowed as e:
        return {'status': 'error', 'errors': [e.message]}, 400


@app.route('/<channel>/<playlist>/edit', methods=['GET', 'POST'])
@lastuser.requires_login
@render_with({'text/html': 'index.html.jinja2'}, json=True)
@load_models(
    (Channel, {'name': 'channel'}, 'channel'),
    (Playlist, {'name': 'playlist', 'channel': 'channel'}, 'playlist'),
    permission='edit',
)
def playlist_edit(channel, playlist):
    form = PlaylistForm(obj=playlist)
    form.channel = channel
    if request.method == 'GET':
        html_form = render_form(
            form=form,
            title=_("Edit Playlist"),
            submit=_("Save"),
            cancel_url=playlist.url_for(),
            ajax=False,
            with_chrome=False,
        ).get_data(as_text=True)
        return {'playlist': dict(playlist.current_access()), 'form': html_form}
    if not playlist.banner_ad_filename:
        del form.delete_banner_ad
    old_playlist_banner_ad_filename = playlist.banner_ad_filename
    old_playlist_name = playlist.name
    try:
        if form.validate_on_submit():
            form.populate_obj(playlist)
            if not playlist.name:
                playlist.make_name()
            playlist.banner_ad = playlist.banner_image
            if old_playlist_name != playlist.name:
                redirect_to = PlaylistRedirect.query.filter_by(
                    name=old_playlist_name, channel=channel
                ).first()
                if redirect_to:
                    redirect_to.playlist = playlist
                else:
                    redirect_to = PlaylistRedirect(
                        name=old_playlist_name, channel=channel, playlist=playlist
                    )
                    db.session.add(redirect_to)
            if playlist.banner_ad:
                if playlist.banner_ad_filename != old_playlist_banner_ad_filename:
                    remove_banner_ad(old_playlist_banner_ad_filename)
                playlist.banner_ad_filename = thumbnails.save(
                    return_werkzeug_filestorage(playlist.banner_ad, playlist.title)
                )
            if form.delete_banner_ad and form.delete_banner_ad.data:
                db.session.add(playlist)
                remove_banner_ad(playlist.banner_ad_filename)
                playlist.banner_ad_filename = None
                playlist.banner_ad_url = ""
            db.session.commit()
            return {
                'status': 'ok',
                'doc': _("Edited playlist {title}.").format(title=playlist.title),
                'result': {'url': playlist.url_for()},
            }, 200
        return {'status': 'error', 'errors': form.errors}, 400
    except UploadNotAllowed as e:
        return {'status': 'error', 'errors': {'error': [e.message]}}, 400


@app.route('/<channel>/<playlist>/delete', methods=['GET', 'POST'])
@lastuser.requires_login
@load_models(
    (Channel, {'name': 'channel'}, 'channel'),
    (Playlist, {'name': 'playlist', 'channel': 'channel'}, 'playlist'),
    permission='delete',
)
@render_with({'text/html': 'index.html.jinja2'}, json=True)
def playlist_delete(channel, playlist):
    if request.method == 'GET':
        return {'playlist': dict(playlist.current_access())}
    form = Form()
    if form.validate_on_submit():
        db.session.delete(playlist)
        db.session.commit()
        return {
            'status': 'ok',
            'doc': _("Deleted playlist {title}.").format(title=playlist.title),
            'result': {},
        }
    return {'status': 'error', 'errors': {'error': form.errors}}, 400


@app.route('/<channel>/<playlist>')
@render_with({'text/html': 'index.html.jinja2'}, json=True)
@load_models(
    (Channel, {'name': 'channel'}, 'channel'),
    (
        (Playlist, PlaylistRedirect),
        {'name': 'playlist', 'channel': 'channel'},
        'playlist',
    ),
    permission='view',
)
def playlist_view(channel, playlist):
    channel_dict = dict(channel.current_access())
    playlist_dict = dict(playlist.current_access_with_all_videos())
    if playlist.banner_ad_url and playlist.banner_ad_filename:
        playlist_dict.update(
            {
                'banner_ad_url': playlist.banner_ad_url,
                'banner_ad_filename': url_for(
                    'static', filename='thumbnails/' + playlist.banner_ad_filename
                ),
            }
        )
    return {'channel': channel_dict, 'playlist': playlist_dict}


@app.route('/<channel>/<playlist>/feed')
@load_models(
    (Channel, {'name': 'channel'}, 'channel'),
    (Playlist, {'name': 'playlist', 'channel': 'channel'}, 'playlist'),
    permission='view',
)
def playlist_feed(channel, playlist):
    videos = list(playlist.videos)[::-1]
    return Response(
        render_template(
            'feed.xml',
            channel=channel,
            playlist=playlist,
            videos=videos,
            feed_url=playlist.url_for(_external=True),
            updated=max(
                [v.updated_at for v in playlist.videos] or [utcnow()]
            ).isoformat(),
        ),
        content_type='application/atom+xml; charset=utf-8',
    )


@app.route('/<channel>/import', methods=['GET', 'POST'])
@lastuser.requires_login
@render_with({'text/html': 'index.html.jinja2'}, json=True)
@load_model(Channel, {'name': 'channel'}, 'channel', permission='new-playlist')
def playlist_import(channel):
    form = PlaylistImportForm()
    form.channel = channel
    if request.method == "GET":
        html_form = render_form(
            form=form,
            title=_("Import Playlist"),
            submit=_("Import"),
            cancel_url=channel.url_for(),
            ajax=True,
            with_chrome=False,
        ).get_data(as_text=True)
        return {'channel': dict(channel.current_access()), 'form': html_form}
    if form.validate_on_submit():
        playlist = Playlist(channel=channel)
        form.populate_obj(playlist)
        try:
            process_playlist(playlist, playlist_url=form.playlist_url.data)
            if not playlist.name:
                playlist.make_name()
            db.session.add(playlist)
            db.session.commit()
            cache.delete('data/featured-channels')
            return {
                'status': 'ok',
                'doc': _("Imported playlist {title}.").format(title=playlist.title),
                'result': {'new_playlist_url': playlist.url_for()},
            }, 201
        except (DataProcessingError, ValueError) as e:
            return {'status': 'error', 'errors': {'playlist_url': [e.message]}}, 400
    return {'status': 'error', 'errors': form.errors}, 400


@app.route('/<channel>/<playlist>/extend', methods=['GET', 'POST'])
@lastuser.requires_login
@render_with({'text/html': 'index.html.jinja2'}, json=True)
@load_models(
    (Channel, {'name': 'channel'}, 'channel'),
    (Playlist, {'name': 'playlist', 'channel': 'channel'}, 'playlist'),
    permission='extend',
)
def playlist_extend(channel, playlist):
    form = PlaylistImportForm()
    form.channel = channel
    if request.method == 'GET':
        html_form = render_form(
            form=form,
            title=_("Playlist extend"),
            submit=_("Save"),
            cancel_url=playlist.url_for(),
            ajax=False,
            with_chrome=False,
        ).get_data(as_text=True)
        return {'playlist': dict(playlist.current_access()), 'form': html_form}
    if form.validate_on_submit():
        playlist_url = escape(form.playlist_url.data)
        initial_count = len(playlist.videos)
        process_playlist(playlist_url=playlist_url, playlist=playlist)
        additions = len(playlist.videos) - initial_count
        if additions:
            db.session.commit()
            cache.delete('data/featured-channels')
        return {
            'status': 'ok',
            'doc': _("Added video to playlist {title}.").format(title=playlist.title),
            'result': {},
        }
    return {'status': 'error', 'errors': form.errors}, 400
