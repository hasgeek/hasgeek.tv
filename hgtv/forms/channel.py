# -*- coding: utf-8 -*-

import flask.ext.wtf as wtf
from baseframe.forms import Form, RichTextField

__all__ = ['ChannelForm']


class ChannelForm(Form):
    type = wtf.SelectField(u"Channel type", coerce=int, validators=[wtf.Required()])
    description = RichTextField(u"Description")
