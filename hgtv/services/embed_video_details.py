# -*- coding: utf-8 -*-

from hgtv import app
from hgtv.services.video_details import get_video_details


def get_embed_video_details(channel, playlist, video):
    video_dict = get_video_details(channel, playlist, video)
    video_dict.update({
        'video_iframe': video.embed_video_for(app.config.get('VIDEO_VIEW_MODE', 'view')),
        'video_source': video.video_source,
        'slides_html': video.embed_slides_for('view'),
        'slides_source': video.slides_source
        })
    return video_dict
