# -*- coding: utf-8 -*-

import wtforms
import wtforms.fields.html5
from baseframe.forms import Form, RichTextField


__all__ = ['VideoAddForm', 'VideoEditForm', 'VideoVideoForm', 'VideoSlidesForm', 'VideoActionForm', 'VideoCsrfForm', 'VideoSlidesSyncForm']


class VideoAddForm(Form):
    video_url = wtforms.fields.html5.URLField(u"Video URL", validators=[wtforms.validators.Required()])
    slides_url = wtforms.fields.html5.URLField(u"Slides URL", validators=[wtforms.validators.Optional()])


class VideoEditForm(Form):
    title = wtforms.TextField(u"Title", validators=[wtforms.validators.Required()],
        description=u"Video title, without the speakers’ names")
    description = RichTextField(u'Description',
        description=u"Summary of this video's content")


class VideoVideoForm(Form):
    video_url = wtforms.fields.html5.URLField(u"Video URL", validators=[wtforms.validators.Required()])


class VideoSlidesForm(Form):
    slides_url = wtforms.fields.html5.URLField(u"Slides URL", validators=[wtforms.validators.Optional()])


class VideoSlidesSyncForm(Form):
    video_slides_mapping = wtforms.TextAreaField(u"Video slides mapping",
                            description=u'Mapping of Video timing in seconds and slide number. E.g {"0": 1, "10": 2}')


class VideoActionForm(Form):
    action = wtforms.HiddenField("Action", validators=[wtforms.validators.Required("You must specify an action")])

    def validate_action(self, field):
        if field.data not in ['star', 'queue', 'like', 'dislike']:
            raise wtforms.ValidationError("Unknown action requested")


class VideoCsrfForm(Form):
    pass
