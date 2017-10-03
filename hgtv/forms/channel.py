# -*- coding: utf-8 -*-

import wtforms
from baseframe.forms import Form, TinyMce4Field

__all__ = ['ChannelForm']


class ChannelForm(Form):
    type = wtforms.SelectField(u"Channel type", coerce=int, validators=[wtforms.validators.Required()])
    description = TinyMce4Field(u"Description", tinymce_options={'height': 200, 'plugins': 'autoresize', 'autoresize_min_height': 150, 'autoresize_max_height': 200})
    channel_logo = wtforms.FileField(u"Channel logo", description="Optional - Channel logos are shown on the homepage when the channel is featured")
    delete_logo = wtforms.BooleanField(u"Remove existing logo?")
