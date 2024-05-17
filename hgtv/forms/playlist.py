import re

from flask import request
from flask_uploads import UploadNotAllowed
from PIL import Image

from baseframe import _, __, forms

from ..models import Playlist

__all__ = ['PlaylistForm', 'PlaylistAddForm', 'PlaylistImportForm']


invalid_name = re.compile(r'[^\w._-]', re.UNICODE)
youtube_playlist_regex = re.compile(
    r'(http|https)://www.youtube.com/playlist?([0-9A-Za-z]+.)', re.UNICODE
)
BANNER_AD_ALLOWED_SIZE = (728, 90)


class PlaylistForm(forms.Form):
    title = forms.StringField(
        __("Title"),
        validators=[forms.validators.DataRequired()],
        description=__("The name of your playlist"),
    )
    name = forms.StringField(
        __("URL Name"),
        description=__("Optional. Will be automatically generated if left blank"),
    )
    description = forms.TinyMce4Field(__("Description"))
    recorded_date = forms.DateField(
        __("Recorded date"),
        description=__(
            "Date on which the videos in this playlist were recorded, if applicable"
        ),
    )
    published_date = forms.DateField(
        __("Published date"),
        validators=[forms.validators.DataRequired()],
        description=__("Date on which this playlist was created or made public"),
    )
    public = forms.BooleanField(__("This playlist is public"), default=True)
    banner_image = forms.FileField(
        __("Playlist banner ad"),
        description=__("Optional - Ad will be displayed in playlist page"),
    )
    banner_ad_url = forms.URLField(
        __("Banner Ad URL"), description=__("URL to which user should be redirected to")
    )
    delete_banner_ad = forms.BooleanField(__("Delete existing ad?"))

    def validate_name(self, field):
        if invalid_name.search(field.data):
            raise forms.validators.ValidationError(
                __("The name cannot have spaces or non-alphanumeric characters")
            )
        existing = Playlist.query.filter_by(
            channel=self.channel, name=field.data
        ).first()
        if existing and existing.id != self.edit_id:
            raise forms.validators.ValidationError(__("That name is already in use"))

    def validate_banner_ad(self, field):
        if field.data and 'banner_ad' in request.files:
            requestfile = request.files['banner_ad']
            fileext = requestfile.filename.split('.')[-1].lower()
            if fileext not in ['png', 'jpg', 'jpeg']:
                raise UploadNotAllowed(
                    _("Unsupported file format. Only PNG and JPG are supported")
                )
            img = Image.open(requestfile)
            img.load()
            if not img.size == BANNER_AD_ALLOWED_SIZE:
                raise UploadNotAllowed(
                    _("Banner size should be %sx%s")
                    % (BANNER_AD_ALLOWED_SIZE[0], BANNER_AD_ALLOWED_SIZE[1])
                )


class PlaylistAddForm(forms.Form):
    playlist = forms.SelectField(__("Add to playlist"), coerce=int)


def playlist_validate_url(self, field):
    if not youtube_playlist_regex.search(field.data):
        raise forms.validators.ValidationError(_("Incorrect Youtube Playlist URL"))


class PlaylistImportForm(forms.Form):
    playlist_url = forms.URLField(
        __("Playlist URL"),
        validators=[forms.validators.DataRequired(), playlist_validate_url],
    )
