# -*- coding: utf-8 -*-

from baseframe.forms import Form, RichTextField
import flask.ext.wtf as wtf

__all__ = ['VideoAddForm', 'VideoEditForm', 'VideoVideoForm', 'VideoSlidesForm']


class VideoAddForm(Form):
    video_url = wtf.html5.URLField(u"Video URL", validators=[wtf.Required()])
    slides_url = wtf.html5.URLField(u"Slides URL", validators=[wtf.Optional()])


class VideoEditForm(Form):
    title = wtf.TextField(u"Title", validators=[wtf.Required()],
        description=u"Video title, without the speakers’ names")
    description = RichTextField(u'Description',
        description=u"Summary of this video's content")


class VideoVideoForm(Form):
    video_url = wtf.html5.URLField(u"Video URL", validators=[wtf.Required()])


class VideoSlidesForm(Form):
    slides_url = wtf.html5.URLField(u"Slides URL", validators=[wtf.Optional()])
