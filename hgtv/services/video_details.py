# -*- coding: utf-8 -*-

from flask import url_for, g


def get_video_details(channel, playlist, video):
    video_dict = {
        'title': video.title,
        'thumbnail': url_for('static', filename='thumbnails/' + video.thumbnail_path),
        'url': video.url_for(channel=channel, playlist=playlist),
        'speakers': [speaker.pickername for speaker in video.speakers],
    }
    return video_dict


def get_video_action_urls(channel, playlist, video):
    video_dict = {
        'remove_video_url': video.url_for('remove-video', channel=channel, playlist=playlist) if 'remove-video'
        in playlist.permissions(g.user) and playlist != video.playlist else '',
        'edit_video_url': video.url_for('edit') if 'edit' in g.permissions else '',
        'delete_video_url': video.url_for('delete') if 'delete' in g.permissions else ''
    }
    return video_dict
