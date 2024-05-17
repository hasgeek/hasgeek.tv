from flask import Response, flash, redirect

from baseframe import _
from coaster.auth import current_auth
from coaster.views import get_next_url

from .. import app, lastuser
from ..models import CHANNEL_TYPE, Channel, db


@app.route('/login')
@lastuser.login_handler
def login():
    return {'scope': 'id organizations'}


@app.route('/logout')
@lastuser.logout_handler
def logout():
    flash(_("You are now logged out"), category='info')
    return get_next_url()


@app.route('/login/redirect')
@lastuser.auth_handler
def lastuserauth():
    Channel.update_from_user(
        current_auth.user,
        db.session,
        type_user=CHANNEL_TYPE.PERSON,
        type_org=CHANNEL_TYPE.ORGANIZATION,
    )
    db.session.commit()
    return redirect(get_next_url())


@app.route('/login/notify', methods=['POST'])
@lastuser.notification_handler
def lastusernotify(user):
    Channel.update_from_user(
        user,
        db.session,
        type_user=CHANNEL_TYPE.PERSON,
        type_org=CHANNEL_TYPE.ORGANIZATION,
    )
    db.session.commit()


@lastuser.auth_error_handler
def lastuser_error(error, error_description=None, error_uri=None):
    if error == 'access_denied':
        flash(_("You denied the request to login"), category='error')
        return redirect(get_next_url())
    return Response(
        _("Error: %s\nDescription: %s\nURI: %s")
        % (error, error_description, error_uri),
        mimetype='text/plain',
    )
