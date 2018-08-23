# -*- coding: utf-8 -*-

from baseframe import forms
from ..models import User

from .. import lastuser


__all__ = ['VideoAddForm', 'VideoEditForm', 'VideoActionForm']


class VideoAddForm(forms.Form):
    video_url = forms.URLField(u"Video URL", validators=[forms.validators.DataRequired()])
    slides_url = forms.URLField(u"Slides URL", validators=[forms.validators.Optional()])


class VideoEditForm(forms.Form):
    title = forms.StringField(u"Title", validators=[forms.validators.DataRequired()],
        description=u"Video title, without the speakers’ names")
    description = forms.TinyMce4Field(u'Description',
        description=u"Summary of this video's content")
    speakers = forms.UserSelectMultiField(u"Speakers", validators=[forms.validators.Optional()],
        description=u"Lookup a user by their username or email address",
        usermodel=User, lastuser=lastuser)
    video_url = forms.URLField(u"Video URL", validators=[forms.validators.DataRequired()])
    slides_url = forms.URLField(u"Slides URL", validators=[forms.validators.Optional()])
    video_slides_mapping = forms.TextAreaField(u"Video slides mapping",
                            description=u'Mapping of Video timing in seconds and slide number. E.g {"0": 1, "10": 2}')


class VideoActionForm(forms.Form):
    action = forms.HiddenField("Action", validators=[forms.validators.DataRequired("You must specify an action")])

    def validate_action(self, field):
        if field.data not in ['star', 'queue', 'like', 'dislike']:
            raise forms.ValidationError("Unknown action requested")
