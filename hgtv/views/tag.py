# -*- coding: utf-8 -*-

from flask import render_template
from coaster.views import load_model

from hgtv import app
from hgtv.models import Tag


@app.route('/tag/')
def tag_cloud():
    return render_template('tagcloud.html', tags=Tag.query.order_by('title').all())


@app.route('/tag/<tagname>')
@load_model(Tag, {'name': 'tagname'}, 'tag')
def view_tag(tag):
    return render_template('tag.html', tag=tag)
