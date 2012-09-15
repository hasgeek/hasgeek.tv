# -*- coding: utf-8 -*-

from flask import Response, redirect, flash, g
from coaster.views import get_next_url

from hgtv import app, lastuser
from hgtv.models import db, Channel, CHANNEL_TYPE


@app.route('/login')
@lastuser.login_handler
def login():
    return {'scope': 'id organizations'}


@app.route('/logout')
@lastuser.logout_handler
def logout():
    flash(u"You are now logged out", category='info')
    return get_next_url()


@app.route('/login/redirect')
@lastuser.auth_handler
def lastuserauth():
    # Make channels for the user's organizations
    username = g.user.username or g.user.userid
    channel = Channel.query.filter_by(userid=g.user.userid).first()
    if channel is None:
        channel = Channel(userid=g.user.userid,
            name=g.user.username or g.user.userid,
            title=g.user.fullname,
            type=CHANNEL_TYPE.PERSON)
        db.session.add(channel)
    else:
        if channel.name != username:
            channel.name = username
        if channel.title != g.user.fullname:
            channel.title = g.user.fullname
    for org in g.user.organizations_owned():
        channel = Channel.query.filter_by(userid=org['userid']).first()
        if channel is None:
            channel = Channel(userid=org['userid'],
                name=org['name'],
                title=org['title'],
                type=CHANNEL_TYPE.ORGANIZATION)
            db.session.add(channel)
        else:
            if channel.name != org['name']:
                channel.name = org['name']
            if channel.title != org['title']:
                channel.title = org['title']

    db.session.commit()
    return redirect(get_next_url())


@lastuser.auth_error_handler
def lastuser_error(error, error_description=None, error_uri=None):
    if error == 'access_denied':
        flash("You denied the request to login", category='error')
        return redirect(get_next_url())
    return Response(u"Error: %s\n"
                    u"Description: %s\n"
                    u"URI: %s" % (error, error_description, error_uri),
                    mimetype="text/plain")
