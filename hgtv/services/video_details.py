# -*- coding: utf-8 -*-

from flask import url_for, g
from hgtv import app


def get_video_details(channel, playlist, video):
    video_dict = {
        'url': unicode(video.id) + '-' + unicode(video.name),
        'title': video.title,
        'description': video.description,
        'thumbnail': url_for('static', filename='thumbnails/' + video.thumbnail_path),
        'speakers': [speaker.pickername for speaker in video.speakers],
        'not_part_playlist': {'name': video.playlist.name, 'title': video.playlist.title} if playlist != video.playlist else False
    }
    return video_dict


def get_video_action_permissions(channel, playlist, video):
    video_dict = {
        'action_url': video.url_for('action') if g.user else '',
        'remove_permission': True if 'remove-video'
        in playlist.permissions(g.user) and playlist != video.playlist else False,
        'edit_permission': True if 'edit' in g.permissions else False,
        'delete_permission': True if 'delete' in g.permissions else False,
        'user_playlists_url': url_for('user_playlists', video=video.url_name) if 'edit' in g.permissions else False
    }
    return video_dict


def get_embed_video_details(channel, playlist, video):
    video_dict = get_video_details(channel, playlist, video)
    video_dict.update({
        'video_iframe': video.embed_video_for(app.config.get('VIDEO_VIEW_MODE', 'view')),
        'video_source': video.video_source,
        'slides_html': video.embed_slides_for('view'),
        'slides_source': video.slides_source
        })
    return video_dict


def get_user_playlist(user, video):
    user_playlists = []
    for c in user.channels:
        for p in c.user_playlists:
            playlist_details = {
                'url': url_for('video_playlist_add', channel=c.name, playlist=p.name, video=video.url_name)
            }
    return user_playlist


def get_user_preference(user, video):
    starred_playlist = g.user.channel.playlist_for_starred()
    queue_playlist = g.user.channel.playlist_for_queue()
    liked_playlist = g.user.channel.playlist_for_liked()
    disliked_playlist = g.user.channel.playlist_for_disliked()
    video_flags = {
        'starred': True if starred_playlist and video in starred_playlist.videos else False,
        'queued': True if queue_playlist and video in queue_playlist.videos else False,
        'liked': True if liked_playlist and video in liked_playlist.videos else False,
        'disliked': True if disliked_playlist and video in disliked_playlist.videos else False
    }
    return video_flags
