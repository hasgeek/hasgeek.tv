# -*- coding: utf-8 -*-

import wtforms
from baseframe.forms import Form, RichTextField

__all__ = ['ChannelForm']


class ChannelForm(Form):
    type = wtforms.SelectField(u"Channel type", coerce=int, validators=[wtforms.validators.Required()])
    description = RichTextField(u"Description")
    channel_logo = wtforms.FileField(u"Channel logo", description="Optional - Channel logos are shown on the homepage when the channel is featured")
    delete_logo = wtforms.BooleanField(u"Remove existing logo?")
