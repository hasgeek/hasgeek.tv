# -*- coding: utf-8 -*-

from baseframe.forms import Form, RichTextField
import flask.ext.wtf as wtf

__all__ = ['VideoAddForm', 'VideoEditForm']


class VideoAddForm(Form):
    video_url = wtf.html5.URLField('Video URL', validators=[wtf.Required()])
    slides_url = wtf.html5.URLField('Slides URL', validators=[wtf.Optional()])


class VideoEditForm(Form):
    title = wtf.TextField('Title', validators=[wtf.Required()])
    description = RichTextField('Description')
    slides_url = wtf.html5.URLField('Slides URL', validators=[wtf.Optional()])
