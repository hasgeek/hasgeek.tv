# -*- coding: utf-8 -*-

import wtforms
from baseframe.forms import Form, TinyMce4Field

__all__ = ['ChannelForm']


class ChannelForm(Form):
    type = wtforms.SelectField(u"Channel type", coerce=int, validators=[wtforms.validators.Required()])
    description = TinyMce4Field(u"Description")
    bio = wtforms.TextField(u"Bio", validators=[wtforms.validators.Optional()],
        description=u"This text is the short description of the channel shown on the homepage")
    channel_logo = wtforms.FileField(u"Channel logo", description="Optional - Channel logos are shown on the homepage when the channel is featured")
    channel_banner_url = wtforms.fields.html5.URLField(u"Channel banner image url", validators=[wtforms.validators.Optional()])
    delete_logo = wtforms.BooleanField(u"Remove existing logo?")
