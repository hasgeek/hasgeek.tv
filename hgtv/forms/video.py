# -*- coding: utf-8 -*-

from baseframe.forms import Form
import flask.ext.wtf as wtf

__all__ = ['VideoAddForm', 'VideoEditForm']

class VideoAddForm(Form):
    url = wtf.TextField('Video URL', validators=[wtf.Required()])


class VideoEditForm(Form):
    description = wtf.TextAreaField('Description')
    url = wtf.TextField('Video URL', validators=[wtf.Required()])
    slides = wtf.TextField('Slides URL')
