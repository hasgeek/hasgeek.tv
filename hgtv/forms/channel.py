from baseframe import __, forms

__all__ = ['ChannelForm']


class ChannelForm(forms.Form):
    type = forms.SelectField(  # noqa: A003
        __("Channel type"), coerce=int, validators=[forms.validators.DataRequired()]
    )
    description = forms.TinyMce4Field(__("Description"))
    bio = forms.StringField(
        __("Bio"),
        description=__(
            "This text is the short description of the channel shown on the homepage"
        ),
    )
    channel_logo = forms.FileField(
        __("Channel logo"),
        description=__(
            "Optional - Channel logos are shown on the homepage when the channel is featured"
        ),
    )
    channel_banner_url = forms.URLField(__("Channel banner image url"))
    delete_logo = forms.BooleanField(__("Remove existing logo?"))
