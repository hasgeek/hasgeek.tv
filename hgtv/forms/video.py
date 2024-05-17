from baseframe import __, forms

from .. import lastuser
from ..models import User

__all__ = ['VideoAddForm', 'VideoEditForm', 'VideoActionForm']


class VideoAddForm(forms.Form):
    video_url = forms.URLField(
        __("Video URL"), validators=[forms.validators.DataRequired()]
    )
    slides_url = forms.URLField(__("Slides URL"))


class VideoEditForm(forms.Form):
    title = forms.StringField(
        __("Title"),
        validators=[forms.validators.DataRequired()],
        description=__("Video title, without the speakers’ names"),
    )
    description = forms.TinyMce4Field(
        __("Description"), description=__("Summary of this video's content")
    )
    speakers = forms.UserSelectMultiField(
        __("Speakers"),
        description=__("Lookup a user by their username or email address"),
        usermodel=User,
        lastuser=lastuser,
    )
    video_url = forms.URLField(
        __("Video URL"), validators=[forms.validators.DataRequired()]
    )
    slides_url = forms.URLField(__("Slides URL"))
    video_slides_mapping = forms.TextAreaField(
        __("Video slides mapping"),
        description=__(
            'Mapping of video timing in seconds and slide number. E.g {"0": 1, "10": 2}'
        ),
    )


class VideoActionForm(forms.Form):
    action = forms.HiddenField(
        __("Action"),
        validators=[forms.validators.DataRequired(__("You must specify an action"))],
    )

    def validate_action(self, field):
        if field.data not in ['star', 'queue', 'like', 'dislike']:
            raise forms.ValidationError(__("Unknown action requested"))
