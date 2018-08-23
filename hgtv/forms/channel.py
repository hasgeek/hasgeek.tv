# -*- coding: utf-8 -*-

from baseframe import forms

__all__ = ['ChannelForm']


class ChannelForm(forms.Form):
    type = forms.SelectField(u"Channel type", coerce=int, validators=[forms.validators.DataRequired()])
    description = forms.TinyMce4Field(u"Description")
    bio = forms.StringField(u"Bio", validators=[forms.validators.Optional()],
        description=u"This text is the short description of the channel shown on the homepage")
    channel_logo = forms.FileField(u"Channel logo", description="Optional - Channel logos are shown on the homepage when the channel is featured")
    channel_banner_url = forms.URLField(u"Channel banner image url", validators=[forms.validators.Optional()])
    delete_logo = forms.BooleanField(u"Remove existing logo?")
