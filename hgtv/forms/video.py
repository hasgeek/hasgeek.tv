# -*- coding: utf-8 -*-

import wtforms
import wtforms.fields.html5
from baseframe import forms
from ..models import User

from .. import lastuser


__all__ = ['VideoAddForm', 'VideoEditForm', 'VideoActionForm']


class VideoAddForm(forms.Form):
    video_url = wtforms.fields.html5.URLField(u"Video URL", validators=[wtforms.validators.Required()])
    slides_url = wtforms.fields.html5.URLField(u"Slides URL", validators=[wtforms.validators.Optional()])


class VideoEditForm(forms.Form):
    title = wtforms.TextField(u"Title", validators=[wtforms.validators.Required()],
        description=u"Video title, without the speakers’ names")
    description = forms.TinyMce4Field(u'Description',
        description=u"Summary of this video's content")
    speakers = forms.UserSelectMultiField(u"Speakers", validators=[wtforms.validators.Optional()],
        description=u"Lookup a user by their username or email address",
        usermodel=User, lastuser=lastuser)
    video_url = wtforms.fields.html5.URLField(u"Video URL", validators=[wtforms.validators.Required()])
    slides_url = wtforms.fields.html5.URLField(u"Slides URL", validators=[wtforms.validators.Optional()])
    video_slides_mapping = wtforms.TextAreaField(u"Video slides mapping",
                            description=u'Mapping of Video timing in seconds and slide number. E.g {"0": 1, "10": 2}')


class VideoActionForm(forms.Form):
    action = wtforms.HiddenField("Action", validators=[wtforms.validators.Required("You must specify an action")])

    def validate_action(self, field):
        if field.data not in ['star', 'queue', 'like', 'dislike']:
            raise wtforms.ValidationError("Unknown action requested")
