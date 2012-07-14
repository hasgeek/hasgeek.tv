# -*- coding: utf-8 -*-

from flask import render_template, abort, g, flash, url_for
from coaster.views import load_model
from baseframe.forms import render_redirect, render_form

from hgtv import app
from hgtv.views.login import lastuser
from hgtv.forms import ChannelForm
from hgtv.models import Channel, db
from hgtv.models.channel import channel_types


@app.route('/<channel>/')
@load_model(Channel, {'name': 'channel'}, 'channel')
def channel_view(channel):
    #videos = (channel.videos + Video.query.filter(Video.channel == channel).limit(3).all())[:3]
    return render_template('channel.html', channel=channel)


@app.route('/<channel>/edit', methods=['GET', 'POST'])
@lastuser.requires_login
@load_model(Channel, {'name': 'channel'}, 'channel')
def channel_edit(channel):
    if channel.userid not in g.user.user_organizations_owned_ids():
        abort(403)
    form = ChannelForm(obj=channel)
    if channel.userid == g.user.userid:
        form.type.choices = [(1, channel_types[1])]
    else:
        choices = channel_types.items()
        choices.sort()
        choices.pop(0)
        choices.pop(0)
        form.type.choices = choices
    if form.validate_on_submit():
        form.populate_obj(channel)
        db.session.commit()
        flash(u"Edited description for channel", 'success')
        return render_redirect(url_for('channel_view', channel=channel.name), code=303)
    return render_form(form=form, title=u"Edit channel", submit=u"Save",
        cancel_url=url_for('channel_view', channel=channel.name), ajax=True)
