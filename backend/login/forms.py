from django import forms

class LoginForm(forms.Form):
    email = forms.EmailField(
        label='Correo',
        widget=forms.EmailInput(attrs={
            'placeholder': 'Correo',
            'autocomplete': 'email',
            'type': 'email',
            'class': 'login-input',
            'style': 'background:transparent;color:#232c36;'
        })
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Contraseña',
            'autocomplete': 'current-password',
            'type': 'password',
            'class': 'login-input',
            'style': 'background:transparent;color:#232c36;'
        })
    )

class UpdateUserForm(forms.Form):
    nombre = forms.CharField(
        label='Nombre',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre completo'
        })
    )
    old_password = forms.CharField(
        label='Contraseña actual',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña actual'
        })
    )
    new_password = forms.CharField(
        label='Nueva contraseña',
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nueva contraseña'
        })
    )

class PasswordResetForm(forms.Form):
    email = forms.EmailField(
        label='Correo',
        widget=forms.EmailInput(attrs={
            'placeholder': 'Correo',
            'autocomplete': 'email',
            'class': 'login-input',
            'style': 'background:transparent;color:#232c36;'
        })
    )

class SetNewPasswordForm(forms.Form):
    password = forms.CharField(
        label='Nueva contraseña',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Nueva contraseña',
            'class': 'login-input',
            'style': 'background:transparent;color:#232c36;'
        })
    )