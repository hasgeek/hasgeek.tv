# -*- coding: utf-8 -*-

from baseframe.forms import Form
import flask.ext.wtf as wtf

__all__ = ['PlaylistForm', 'PlaylistAddForm']


class PlaylistForm(Form):
    title = wtf.TextField('Title', validators=[wtf.Required()])

class PlaylistAddForm(Form):
    playlist = wtf.SelectField('Add to playlist', coerce=int)
