# -*- coding: utf-8 -*-

from urlparse import urlparse, parse_qs
from socket import gaierror
import requests
from flask import render_template, flash, escape
from coaster.views import load_model, load_models
from baseframe.forms import render_redirect, render_form, render_delete_sqla
from hgtv import app
from hgtv.views.login import lastuser
from hgtv.forms import PlaylistForm, PlaylistImportForm
from hgtv.models import db, Channel, Playlist, Video
from hgtv.views.video import DataProcessingError


#helpers
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
                # first two character of playlist id says what type of playlist, ignore them
                playlist_id = parse_qs(parsed.query)['list'][0][2:]
                r = requests.get('http://gdata.youtube.com/feeds/api/playlists/%s?v=2&alt=json' % playlist_id)
                if r.json is None:
                    raise DataProcessingError("Unable to fetch data, please check the youtube url")
                else:
                    # fetch playlist info
                    playlist.title = r.json['feed']['title']['$t']
                    if 'media$description' in r.json['feed']['media$group']:
                        playlist.description = escape(r.json['feed']['media$group']['media$description']['$t'])
                    try:
                        #exception to catch empty playlist
                        for item in r.json['feed']['entry']:
                            video = Video(playlist=playlist)
                            video.title = item['title']['$t']
                            video.video_url = item['media$group']['media$player']['url']
                            if 'media$description' in item['media$group']:
                                video.description = escape(item['media$group']['media$description']['$t'])
                            for video_content in item['media$group']['media$thumbnail']:
                                if video_content['yt$name'] == 'mqdefault':
                                    video.thumbnail_url = video_content['url']  # .replace('hqdefault', 'mqdefault')
                            video.video_sourceid = item['media$group']['yt$videoid']['$t']
                            video.video_source = u"youtube"
                            video.make_name()
                            playlist.videos.append(video)
                    except KeyError:
                        raise DataProcessingError("Empty Playlist")
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
    permission='edit'
    )
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
    permission='view'
    )
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
            process_playlist(playlist, playlist_url=form.playlist_url.data)
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
