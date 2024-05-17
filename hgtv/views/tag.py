from flask import render_template

from coaster.views import load_model

from .. import app
from ..models import Tag


@app.route('/tag/')
def tag_cloud():
    return render_template(
        'tagcloud.html.jinja2', tags=Tag.query.order_by(Tag.title).all()
    )


@app.route('/tag/<tagname>')
@load_model(Tag, {'name': 'tagname'}, 'tag')
def view_tag(tag):
    return render_template('tag.html.jinja2', tag=tag)
