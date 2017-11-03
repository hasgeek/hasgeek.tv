# -*- coding: utf-8 -*-

from hgtv.services.video_details import get_video_details


def get_related_video_details(channel, playlist, video):
    videos_dict = []
    if playlist.next(video=video):
        videos_dict.append(get_video_details(channel, playlist, playlist.next(video=video)))
    if playlist.prev(video=video):
        videos_dict.append(get_video_details(channel, playlist, playlist.prev(video=video)))
    return videos_dict
