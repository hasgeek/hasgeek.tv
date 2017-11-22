# -*- coding: utf-8 -*-


def get_channel_details(channel):
    channel_dict = {
        'name': channel.name,
        'title': channel.title,
        'description': channel.description
    }
    return channel_dict
