from django import forms

from ..view.models import Stream


class EditForm(forms.ModelForm):
    class Meta:
        model = Stream
        fields = [
            "source_name",
            "description",
            "categories",
        ]
        labels = {
            "source_name": "Name of Originating Organization",
            "description": "Description of Stream",
            "categories": "Categories",
        }
        not_required = (
            "categories",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.Meta.not_required:
            self.fields[field].required = False

        # Add css classes to the elements
        for field in self.fields:
            self.fields[field].widget.attrs.update({"class": "form-control"})
