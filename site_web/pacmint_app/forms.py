from django import forms
from .models import Player


# class PlayerRegistrationForm(forms.ModelForm):
#     password = forms.CharField(widget=forms.PasswordInput, max_length=50)
#     confirm_password = forms.CharField(widget=forms.PasswordInput, max_length=50)
#
#     class Meta:
#         model = Player
#         fields = ['username', 'email']  # Ajouter ici tous les champs que tu veux dans ton formulaire d'inscription
#
#     def clean(self):
#         cleaned_data = super().clean()
#         password = cleaned_data.get("password")
#         confirm_password = cleaned_data.get("confirm_password")
#
#         # Vérifier que les mots de passe correspondent
#         if password != confirm_password:
#             raise forms.ValidationError("Les mots de passe ne correspondent pas.")
#         return cleaned_data


class PlayerRegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=50, label="Pseudonyme")
    password = forms.CharField(widget=forms.PasswordInput, max_length=50, label="Mot de passe")
    confirm_password = forms.CharField(widget=forms.PasswordInput, max_length=50, label="Confirmez le mot de passe")
    email = forms.EmailField(max_length=100, label="Email")

    class Meta:
        model = Player
        fields = ['username', 'password','confirm_password','email']
