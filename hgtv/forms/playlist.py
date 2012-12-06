
# -*- coding: utf-8 -*-

import re
from datetime import date
import flask.ext.wtf as wtf
from baseframe.forms import Form, RichTextField

from hgtv.models import Playlist

__all__ = ['PlaylistForm', 'PlaylistAddForm', 'PlaylistImportForm']


invalid_name = re.compile(r'[^\w._-]', re.UNICODE)


class PlaylistForm(Form):
    title = wtf.TextField(u"Title", validators=[wtf.Required()],
        description=u"The name of your playlist")
    short_title = wtf.TextField(u"Short title", validators=[wtf.Optional()],
        description=u"Shorter title, displayed next to the channel's name when viewing a video")
    name = wtf.TextField(u"URL Name", validators=[wtf.Optional()],
        description=u"Optional. Will be automatically generated if left blank")
    description = RichTextField(u"Description")
    recorded_date = wtf.DateField(u"Recorded date", validators=[wtf.Optional()],
        description=u"Date on which the videos in this playlist were recorded, if applicable")
    published_date = wtf.DateField(u"Published date", validators=[wtf.Required()],
        default=date.today(),
        description=u"Date on which this playlist was created or made public")
    public = wtf.BooleanField(u"This playlist is public", default=True)

    def validate_name(self, field):
        if invalid_name.search(field.data):
            raise wtf.ValidationError("The name cannot have spaces or non-alphanumeric characters")
        existing = Playlist.query.filter_by(channel=self.channel, name=field.data).first()
        if existing and existing.id != self.edit_id:
            raise wtf.ValidationError("That name is already in use")


class PlaylistAddForm(Form):
    playlist = wtf.SelectField('Add to playlist', coerce=int)


def playlist_validate_url(self, field):
    youtube_regex = re.compile(r'(http|https)://www.youtube.com/playlist?([0-9A-Za-z]+.)', re.UNICODE)
    if not youtube_regex.search(field.data):
        raise wtf.ValidationError("InCorrect Youtube Playlist URL")


class PlaylistImportForm(Form):
    playlist_url = wtf.html5.URLField(u"Playlist URL", validators=[wtf.Required(), playlist_validate_url])

