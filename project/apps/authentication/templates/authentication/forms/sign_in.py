from django import forms


class SignInForm(forms.Form):
    username = forms.CharField(label='Usuário', widget=forms.TextInput(attrs={
        'placeholder': 'Digite seu nome de usuário'
    }))
    password = forms.CharField(label='Senha', widget=forms.PasswordInput(attrs={
        'placeholder': 'Digite sua senha'
    }))