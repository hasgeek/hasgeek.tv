from flask import url_for
from pytz import utc

from baseframe import _
from baseframe.forms import render_message
from coaster.views import render_with

from .. import app
from ..models import Channel


@app.template_filter('shortdate')
def shortdate(date):
    return utc.localize(date).astimezone(app.config['tz']).strftime('%e %b')


@app.template_filter('longdate')
def longdate(date):
    return utc.localize(date).astimezone(app.config['tz']).strftime('%e %B %Y')


@app.route('/')
@render_with({'text/html': 'index.html.jinja2'}, json=True)
def index():
    livestream = {
        'enable': bool(app.config.get('LIVESTREAM', [])),
        'streams': app.config.get('LIVESTREAM', []),
    }
    channel_dict = []
    for channel in Channel.get_featured():
        channel_dict.append(
            {
                'name': channel.name,
                'title': channel.title,
                'logo': (
                    url_for(
                        'static', filename='thumbnails/' + channel.channel_logo_filename
                    )
                    if channel.channel_logo_filename
                    else url_for('static', filename='img/sample-logo.png')
                ),
                'banner_url': (
                    channel.channel_banner_url if channel.channel_banner_url else ""
                ),
                'bio': channel.bio if channel.bio else '',
            }
        )
    return {'channels': channel_dict, 'livestream': livestream}


@app.route('/search')
def search():
    return render_message(
        title=_("No search"), message=_("Search hasn’t been implemented yet.")
    )


@app.route('/service-worker.js', methods=['GET'])
def sw():
    return app.send_static_file('service-worker.js')


@app.route('/manifest.json', methods=['GET'])
def manifest():
    return app.send_static_file('manifest.json')
