
# -*- coding: utf-8 -*-

import re
from datetime import date
from PIL import Image
from flask import request
import flask.ext.wtf as wtf
from flask.ext.uploads import UploadNotAllowed
from baseframe.forms import Form, RichTextField

from hgtv.models import Playlist

__all__ = ['PlaylistForm', 'PlaylistAddForm', 'PlaylistImportForm']


invalid_name = re.compile(r'[^\w._-]', re.UNICODE)
youtube_playlist_regex = re.compile(r'(http|https)://www.youtube.com/playlist?([0-9A-Za-z]+.)', re.UNICODE)
BANNER_AD_ALLOWED_SIZE = (728, 90)


class PlaylistForm(Form):
    title = wtf.TextField(u"Title", validators=[wtf.Required()],
        description=u"The name of your playlist")
    short_title = wtf.TextField(u"Short title", validators=[wtf.Optional()],
        description=u"Shorter title, displayed next to the channel's name when viewing a video")
    name = wtf.TextField(u"URL Name", validators=[wtf.Optional()],
        description=u"Optional. Will be automatically generated if left blank")
    description = RichTextField(u"Description")
    recorded_date = wtf.DateField(u"Recorded date", validators=[wtf.Optional()],
        description=u"Date on which the videos in this playlist were recorded, if applicable")
    published_date = wtf.DateField(u"Published date", validators=[wtf.Required()],
        default=date.today(),
        description=u"Date on which this playlist was created or made public")
    public = wtf.BooleanField(u"This playlist is public", default=True)
    banner_image = wtf.FileField(u"Playlist banner ad", description="Optional - Ad will be displayed in playlist page", validators=[wtf.Optional()])
    banner_ad_url = wtf.html5.URLField(u"Banner Ad URL", description="URL to which user should be redirected to", validators=[wtf.Optional()])
    delete_banner_ad = wtf.BooleanField(u"Delete existing ad?")

    def validate_name(self, field):
        if invalid_name.search(field.data):
            raise wtf.ValidationError("The name cannot have spaces or non-alphanumeric characters")
        existing = Playlist.query.filter_by(channel=self.channel, name=field.data).first()
        if existing and existing.id != self.edit_id:
            raise wtf.ValidationError("That name is already in use")

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
    playlist = wtf.SelectField('Add to playlist', coerce=int)


def playlist_validate_url(self, field):
    if not youtube_playlist_regex.search(field.data):
        raise wtf.ValidationError("InCorrect Youtube Playlist URL")


class PlaylistImportForm(Form):
    playlist_url = wtf.html5.URLField(u"Playlist URL", validators=[wtf.Required(), playlist_validate_url])
