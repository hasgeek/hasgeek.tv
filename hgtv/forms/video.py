# -*- coding: utf-8 -*-

from baseframe import forms

from .. import lastuser
from ..models import User

__all__ = ['VideoAddForm', 'VideoEditForm', 'VideoActionForm']


class VideoAddForm(forms.Form):
    video_url = forms.URLField(
        "Video URL", validators=[forms.validators.DataRequired()]
    )
    slides_url = forms.URLField("Slides URL")


class VideoEditForm(forms.Form):
    title = forms.StringField(
        "Title",
        validators=[forms.validators.DataRequired()],
        description="Video title, without the speakers’ names",
    )
    description = forms.TinyMce4Field(
        'Description', description="Summary of this video's content"
    )
    speakers = forms.UserSelectMultiField(
        "Speakers",
        description="Lookup a user by their username or email address",
        usermodel=User,
        lastuser=lastuser,
    )
    video_url = forms.URLField(
        "Video URL", validators=[forms.validators.DataRequired()]
    )
    slides_url = forms.URLField("Slides URL")
    video_slides_mapping = forms.TextAreaField(
        "Video slides mapping",
        description='Mapping of Video timing in seconds and slide number. E.g {"0": 1, "10": 2}',
    )


class VideoActionForm(forms.Form):
    action = forms.HiddenField(
        "Action",
        validators=[forms.validators.DataRequired("You must specify an action")],
    )

    def validate_action(self, field):
        if field.data not in ['star', 'queue', 'like', 'dislike']:
            raise forms.ValidationError("Unknown action requested")
