from django import forms
from django.contrib.auth import authenticate


class SignInForm(forms.Form):
    username = forms.CharField(label='Usuário', widget=forms.TextInput(attrs={
        'placeholder': 'Digite seu nome de usuário'
    }))
    password = forms.CharField(label='Senha', widget=forms.PasswordInput(attrs={
        'placeholder': 'Digite sua senha'
    }))

    def clean(self):
        cleaned = super().clean()
        credentials = {f: cleaned.get(f) for f in self.fields}
        user = authenticate(**credentials)
        if user is None:
            raise forms.ValidationError("Your credentials are incorrect.")
        self.user = user
        return cleaned