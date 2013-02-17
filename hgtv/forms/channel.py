# -*- coding: utf-8 -*-

import flask.ext.wtf as wtf
from baseframe.forms import Form, RichTextField

__all__ = ['ChannelForm']


class ChannelForm(Form):
    type = wtf.SelectField(u"Channel type", coerce=int, validators=[wtf.Required()])
    description = RichTextField(u"Description")
    channel_logo = wtf.FileField(u"Channel logo", description="Optional - Channel logo will appear in channel page, 320 * 240 px")
    delete_logo = wtf.BooleanField(u"Check to remove logo", description="Check the box to remove logo")
