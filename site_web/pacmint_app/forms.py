from django import forms
from .models import Player
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field

class PlayerRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, max_length=50, label="Mot de passe", required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput, max_length=50, label="Confirmez le mot de passe", required=True)

    class Meta:
        model = Player
        fields = ['username', 'email', 'password', 'confirm_password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'S\'inscrire', css_class='btn btn-success'))
        self.helper.layout = Layout(
            Field('username', css_class='form-control'),
            Field('email', css_class='form-control'),
            Field('password', css_class='form-control'),
            Field('confirm_password', css_class='form-control'),
        )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        return cleaned_data


class PlayerLoginForm(forms.Form):
    username = forms.CharField(max_length=50, label="Pseudonyme", required=True)
    password = forms.CharField(widget=forms.PasswordInput, max_length=50, label="Mot de passe", required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('username', css_class='form-control'),
            Field('password', css_class='form-control'),
            Submit('submit', 'Se connecter', css_class='btn btn-primary')
        )