
# -*- coding: utf-8 -*-

import re
from PIL import Image
from flask import request
from flask_uploads import UploadNotAllowed
from baseframe import forms
from hgtv.models import Playlist

__all__ = ['PlaylistForm', 'PlaylistAddForm', 'PlaylistImportForm']


invalid_name = re.compile(r'[^\w._-]', re.UNICODE)
youtube_playlist_regex = re.compile(r'(http|https)://www.youtube.com/playlist?([0-9A-Za-z]+.)', re.UNICODE)
BANNER_AD_ALLOWED_SIZE = (728, 90)


class PlaylistForm(forms.Form):
    title = forms.StringField(u"Title", validators=[forms.validators.DataRequired()],
        description=u"The name of your playlist")
    name = forms.StringField(u"URL Name", validators=[forms.validators.Optional()],
        description=u"Optional. Will be automatically generated if left blank")
    description = forms.TinyMce4Field(u"Description", validators=[forms.validators.Optional()])
    recorded_date = forms.DateField(u"Recorded date", validators=[forms.validators.Optional()],
        description=u"Date on which the videos in this playlist were recorded, if applicable")
    published_date = forms.DateField(u"Published date", validators=[forms.validators.DataRequired()],
        description=u"Date on which this playlist was created or made public")
    public = forms.BooleanField(u"This playlist is public", default=True)
    banner_image = forms.FileField(u"Playlist banner ad", description="Optional - Ad will be displayed in playlist page", validators=[forms.validators.Optional()])
    banner_ad_url = forms.URLField(u"Banner Ad URL", description="URL to which user should be redirected to", validators=[forms.validators.Optional()])
    delete_banner_ad = forms.BooleanField(u"Delete existing ad?")

    def validate_name(self, field):
        if invalid_name.search(field.data):
            raise forms.validators.ValidationError("The name cannot have spaces or non-alphanumeric characters")
        existing = Playlist.query.filter_by(channel=self.channel, name=field.data).first()
        if existing and existing.id != self.edit_id:
            raise forms.validators.ValidationError("That name is already in use")

    def validate_banner_ad(self, field):
        if field.data and 'banner_ad' in request.files:
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


class PlaylistAddForm(forms.Form):
    playlist = forms.SelectField('Add to playlist', coerce=int)


def playlist_validate_url(self, field):
    if not youtube_playlist_regex.search(field.data):
        raise forms.validators.ValidationError("InCorrect Youtube Playlist URL")


class PlaylistImportForm(forms.Form):
    playlist_url = forms.URLField(u"Playlist URL", validators=[forms.validators.DataRequired(), playlist_validate_url])
