# -*- coding: utf-8 -*-

from baseframe.forms import Form
import flask.ext.wtf as wtf

__all__ = ['VideoAddForm']

class VideoAddForm(Form):
    url = wtf.TextField('Video URL', validators=[wtf.Required()])
