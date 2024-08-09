from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm


# Allows submission of stream descriptions
class DescriptionForm(forms.Form):
    text = forms.CharField(widget=forms.TextInput, max_length=10000, required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['text'].widget.attrs.update({"class": "form-control"})


class CustomLoginForm(AuthenticationForm):
    """
    Custom login form. It will allow us to add some styling to the login form.

    References:
        Customizing Django's Built-in Login Form, https://www.notimedad.dev/customizing-django-builtin-login-form/
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({"class": "form-control"})
        self.fields['password'].widget.attrs.update({"class": "form-control"})


class CustomUserCreationForm(UserCreationForm):
    """
    Custom user creation form. It will allow us to add some styling to the user creation form.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({"class": "form-control"})
        self.fields['password1'].widget.attrs.update({"class": "form-control"})
        self.fields['password2'].widget.attrs.update({"class": "form-control"})
