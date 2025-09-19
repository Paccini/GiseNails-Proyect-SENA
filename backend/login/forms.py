from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={
            'placeholder': 'Usuario',
            'autocomplete': 'username',
            'type': 'text',
            'style': 'background:transparent;color:#fff;'
        })
    )
    password = forms.CharField(
        label='',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Contraseña',
            'autocomplete': 'current-password',
            'type': 'password',
            'style': 'background:transparent;color:#fff;'
        })
    )