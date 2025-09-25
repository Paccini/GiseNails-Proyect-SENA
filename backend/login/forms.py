from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={
            'placeholder': 'Correo',
            'autocomplete': 'email',
            'type': 'email',
            'class': 'login-input',  # <--- agrega esta clase
            'style': 'background:transparent;color:#232c36;'
        })
    )
    password = forms.CharField(
        label='',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Contraseña',
            'autocomplete': 'current-password',
            'type': 'password',
            'class': 'login-input',
            'style': 'background:transparent;color:#232c36;'
        })
    )