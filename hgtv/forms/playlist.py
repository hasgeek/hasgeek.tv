# -*- coding: utf-8 -*-

from baseframe.forms import Form
import flask.ext.wtf as wtf

__all__ = ['PlaylistForm']


class PlaylistForm(Form):
    title = wtf.TextField('Title', validators=[wtf.Required()])
