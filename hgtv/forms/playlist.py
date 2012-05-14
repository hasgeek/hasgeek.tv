# -*- coding: utf-8 -*-

import re
from baseframe.forms import Form, RichTextField
import flask.ext.wtf as wtf

from hgtv.models import Playlist

__all__ = ['PlaylistForm', 'PlaylistAddForm']


invalid_name = re.compile(r'[^\w._-]', re.UNICODE)


class PlaylistForm(Form):
    title = wtf.TextField(u"Title", validators=[wtf.Required()],
        description=u"The name of your playlist")
    short_title = wtf.TextField(u"Short title", validators=[wtf.Optional()],
        description=u"Shorter title, displayed next to the channel's name when viewing a video")
    name = wtf.TextField(u"URL Name", validators=[wtf.Optional()],
        description=u"Optional. Will be automatically generated if left blank")
    description = RichTextField(u"Description")
    recorded_date = wtf.DateField(u"Recorded date", validators=[wtf.Optional()])
    published_date = wtf.DateField(u"Published date", validators=[wtf.Required()])

    def validate_name(self, field):
        if invalid_name.search(field.data):
            raise wtf.ValidationError("The name cannot have spaces or non-alphanumeric characters")
        if self.edit_obj:
            edit_id = self.edit_obj.id
        else:
            edit_id = None
        existing = Playlist.query.filter_by(channel=self.channel, name=field.data).first()
        if existing and existing.id != edit_id:
            raise wtf.ValidationError("That name is already in use")


class PlaylistAddForm(Form):
    playlist = wtf.SelectField('Add to playlist', coerce=int)
