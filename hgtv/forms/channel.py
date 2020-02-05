# -*- coding: utf-8 -*-

from baseframe import forms

__all__ = ['ChannelForm']


class ChannelForm(forms.Form):
    type = forms.SelectField("Channel type", coerce=int, validators=[forms.validators.DataRequired()])
    description = forms.TinyMce4Field("Description")
    bio = forms.StringField("Bio",
        description="This text is the short description of the channel shown on the homepage")
    channel_logo = forms.FileField("Channel logo",
        description="Optional - Channel logos are shown on the homepage when the channel is featured")
    channel_banner_url = forms.URLField("Channel banner image url")
    delete_logo = forms.BooleanField("Remove existing logo?")
