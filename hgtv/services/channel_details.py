# -*- coding: utf-8 -*-

from flask import g


def get_channel_details(channel):
    channel_dict = {
        'name': channel.name,
        'title': channel.title,
        'description': channel.description
    }
    return channel_dict


def get_channel_action_permissions():
    channel_dict = {
        'new_playlist_permission': True if 'new-playlist' in g.permissions else False,
        'new_video_permission': True if 'new-video' in g.permissions else False
    }
    return channel_dict
