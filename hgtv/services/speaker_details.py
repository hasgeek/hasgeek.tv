# -*- coding: utf-8 -*-


def get_speaker_details(speaker):
    if speaker:
        speaker_dict = {
            'pickername': speaker.pickername,
            # 'externalid': speaker.externalid if speaker.externalid else '',
            'playlist_for_speaking_in': speaker.playlist_for_speaking_in().url_for('view')
        }
    return speaker_dict
