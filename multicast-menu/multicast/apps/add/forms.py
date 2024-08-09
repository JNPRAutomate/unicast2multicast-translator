from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import validate_ipv4_address

from ..view.models import Stream


# Allows authenticated users to manually report a stream
class ManualSubmissionForm(forms.ModelForm):
    amt_relay_other = forms.CharField(max_length=100, required=False, label="Other")

    class Meta:
        model = Stream
        fields = [
            "source",
            "group",
            "udp_port",
            "amt_relay",
            "source_name",
            "description",
            "categories",
        ]
        labels = {
            "source": "Source IP",
            "group": "Group IP",
            "udp_port": "UDP Port",
            "amt_relay": "AMT Relay",
            "source_name": "Name of Originating Organization",
            "description": "Description of Stream",
            "categories": "Categories"
        }
        required = (
            "source",
            "group",
            "amt_relay",
            "source_name",
            "description",
        )
        not_required = (
            "udp_port",
            "categories",
        )

    field_order = ["source",
                   "group",
                   "udp_port",
                   "amt_relay",
                   "amt_relay_other",
                   "source_name",
                   "description",
                   "categories"]

    def __init__(self, *args, **kwargs):
        _relay_list = kwargs.pop('data_list', None)
        super().__init__(*args, **kwargs)

        for field in self.Meta.required:
            self.fields[field].required = True

        for field in self.Meta.not_required:
            self.fields[field].required = False

        self.fields["amt_relay"].widget = forms.Select(choices=_relay_list)

        # Add css classes to the elements
        for field in self.fields:
            self.fields[field].widget.attrs.update({"class": "form-control"})

    def is_valid(self):
        valid = super(ManualSubmissionForm, self).is_valid()
        source = self.cleaned_data.get("source")
        group = self.cleaned_data.get("group")

        unique = not Stream.objects.filter(source=source, group=group).exists()
        if not unique:
            self.add_error("source",
                           "This stream already exists on the platform. Contact an admin if you wish to claim it.")
            self.add_error("group",
                           "This stream already exists on the platform. Contact an admin if you wish to claim it")
            valid = False

        if self.cleaned_data["udp_port"] is not None and self.cleaned_data["udp_port"] <= 0:
            self.add_error("udp_port", "Please enter a positive number.")
            valid = False

        if int(self.cleaned_data["amt_relay"]) == 2 and not self.cleaned_data["amt_relay_other"]:
            self.add_error("amt_relay", "Please specify an AMT relay.")
            valid = False

        return valid


# Allows authenticated users to upload a file to be streamed
class UploadSubmissionForm(forms.ModelForm):
    file_to_stream = forms.FileField(allow_empty_file=False, required=True)

    class Meta:
        model = Stream
        fields = [
            "source_name",
            "description",
            "categories"
        ]
        labels = {
            "source_name": "Name of Originating Organization",
            "description": "Description of Stream",
            "categories": "Categories"
        }
        required = (
            "source_name",
            "description",
        )
        not_required = (
            "categories",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.Meta.required:
            self.fields[field].required = True

        for field in self.Meta.not_required:
            self.fields[field].required = False

        # Add css classes to the elements
        for field in self.fields:
            if field == "file_to_stream":
                self.fields[field].widget.attrs.update({"class": "form-control-file"})
            else:
                self.fields[field].widget.attrs.update({"class": "form-control"})
