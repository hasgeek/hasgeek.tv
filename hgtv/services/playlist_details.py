# -*- coding: utf-8 -*-

from hgtv.services.video_details import get_video_details


def get_playlist_details(channel, playlist, videos_count='all'):
    playlist_dict = {
        'title': playlist.title,
        'url': playlist.url_for(),
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
