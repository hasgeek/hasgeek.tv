# -*- coding: utf-8 -*-

from flask import g
from hgtv.services.video_details import get_video_details


def get_playlist_details(channel, playlist, videos_count='all'):
    playlist_dict = {
        'name': playlist.name,
        'title': playlist.title,
        'description': playlist.description
    }
    if playlist.videos and videos_count != 'none':
        if videos_count == 'featured':
            videos = playlist.videos[:4]
        else:
            videos = playlist.videos
        playlist_dict.update({
            'videos': [get_video_details(channel, playlist, video) for video in videos]
        })
    return playlist_dict


def get_playlist_action_permissions():
    playlist_dict = {
        'delete_permission': True if 'delete' in g.permissions else False,
        'add_video_permission': True if 'new-video' in g.permissions else False,
        'edit_permission': True if 'edit' in g.permissions else False,
        'extend_permission': True if 'extend' in g.permissions else False
    }
    return playlist_dict
