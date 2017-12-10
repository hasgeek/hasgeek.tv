
# -*- coding: utf-8 -*-

import re
from PIL import Image
from flask import request
import wtforms
import wtforms.fields.html5
from flask_uploads import UploadNotAllowed
from baseframe.forms import Form, TinyMce4Field

from hgtv.models import Playlist

__all__ = ['PlaylistForm', 'PlaylistAddForm', 'PlaylistImportForm']


invalid_name = re.compile(r'[^\w._-]', re.UNICODE)
youtube_playlist_regex = re.compile(r'(http|https)://www.youtube.com/playlist?([0-9A-Za-z]+.)', re.UNICODE)
BANNER_AD_ALLOWED_SIZE = (728, 90)


class PlaylistForm(Form):
    title = wtforms.TextField(u"Title", validators=[wtforms.validators.Required()],
        description=u"The name of your playlist")
    name = wtforms.TextField(u"URL Name", validators=[wtforms.validators.Optional()],
        description=u"Optional. Will be automatically generated if left blank")
    description = TinyMce4Field(u"Description", validators=[wtforms.validators.Optional()])
    recorded_date = wtforms.DateField(u"Recorded date", validators=[wtforms.validators.Optional()],
        description=u"Date on which the videos in this playlist were recorded, if applicable")
    published_date = wtforms.DateField(u"Published date", validators=[wtforms.validators.Required()],
        description=u"Date on which this playlist was created or made public")
    public = wtforms.BooleanField(u"This playlist is public", default=True)
    banner_image = wtforms.FileField(u"Playlist banner ad", description="Optional - Ad will be displayed in playlist page", validators=[wtforms.validators.Optional()])
    banner_ad_url = wtforms.fields.html5.URLField(u"Banner Ad URL", description="URL to which user should be redirected to", validators=[wtforms.validators.Optional()])
    delete_banner_ad = wtforms.BooleanField(u"Delete existing ad?")

    def validate_name(self, field):
        if invalid_name.search(field.data):
            raise wtforms.validators.ValidationError("The name cannot have spaces or non-alphanumeric characters")
        existing = Playlist.query.filter_by(channel=self.channel, name=field.data).first()
        if existing and existing.id != self.edit_id:
            raise wtforms.validators.ValidationError("That name is already in use")

    def validate_banner_ad(self, field):
        if field.data:
            requestfile = request.files['banner_ad']
            fileext = requestfile.filename.split('.')[-1].lower()
            if fileext not in [u'png', u'jpg', u'jpeg']:
                raise UploadNotAllowed(u"Unsupported file format. Only PNG and JPG are supported")
            img = Image.open(requestfile)
            img.load()
            if not img.size == BANNER_AD_ALLOWED_SIZE:
                raise UploadNotAllowed(u"Banner size should be %sx%s" % (BANNER_AD_ALLOWED_SIZE[0], BANNER_AD_ALLOWED_SIZE[1]))

    def validate_banner_ad_url(self, field):
        if not field.data:
            raise UploadNotAllowed(u"Banner Ad URL is required")


class PlaylistAddForm(Form):
    playlist = wtforms.SelectField('Add to playlist', coerce=int)


def playlist_validate_url(self, field):
    if not youtube_playlist_regex.search(field.data):
        raise wtforms.validators.ValidationError("InCorrect Youtube Playlist URL")


class PlaylistImportForm(Form):
    playlist_url = wtforms.fields.html5.URLField(u"Playlist URL", validators=[wtforms.validators.Required(), playlist_validate_url])
