# -*- coding: utf-8 -*-


def get_channel_details(channel):
    channel_dict = {
        'title': channel.title,
        'description': channel.description,
        'url': channel.url_for()
    }
    return channel_dict
