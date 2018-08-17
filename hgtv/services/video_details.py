# -*- coding: utf-8 -*-

from flask import url_for, g
from hgtv import app


def get_user_playlist(user, video):
    user_playlists = []
    for c in user.channels:
        for p in c.user_playlists:
            playlist_details = {
                'url': url_for('video_playlist_add', channel=c.name, playlist=p.name, video=video.url_name)
            }
            user_playlists.append(playlist_details)
    return user_playlists
