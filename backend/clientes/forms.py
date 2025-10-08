from django import forms
from django.core.validators import RegexValidator 
from django.contrib.auth.models import User
from .models import Cliente

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = '__all__'

class RegistroClienteForm(forms.ModelForm):
    nombre = forms.CharField(
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z\s]+$', 
                message='El nombre solo puede contener letras y espacios.'
                )
        ],
        widget=forms.TextInput(attrs={
            'placeholder': 'Nombre',
            'autocomplete': 'name',
            'type': 'text',
            'class': 'login-input',
            'style': 'background:transparent;color:#232c36;'
        })
    )
    correo = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'Correo',
            'autocomplete': 'email',
            'type': 'email',
            'class': 'login-input',
            'style': 'background:transparent;color:#232c36;'
        })
    )
    telefono = forms.CharField(
        validators=[
            RegexValidator(
                regex=r'^\+?\d{9,15}$', 
                message='El número de teléfono debe tener entre 9 y 15 dígitos y puede incluir el código de país y no debe tener letras.'
            )
        ],
        widget=forms.TextInput(attrs={
            'placeholder': 'Teléfono',
            'autocomplete': 'tel',
            'type': 'tel',
            'class': 'login-input',
            'style': 'background:transparent;color:#232c36;'
        })
    )

    class Meta:
        model = Cliente
        fields = ['nombre', 'correo', 'telefono']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo agregar el campo password si NO se está editando (no hay instancia)
        if not self.instance.pk:
            self.fields['password'] = forms.CharField(
                widget=forms.PasswordInput(attrs={
                    'placeholder': 'Contraseña',
                    'autocomplete': 'new-password',
                    'type': 'password',
                    'class': 'login-input',
                    'style': 'background:transparent;color:#232c36;'
                })
            )

    def save(self, commit=True):
        cliente = super().save(commit=False)
        # Solo crear el usuario si es registro (no edición)
        if not self.instance.pk:
            user = User.objects.create_user(
                username=self.cleaned_data['correo'],
                email=self.cleaned_data['correo'],
                password=self.cleaned_data['password'],
                first_name=self.cleaned_data['nombre']
            )
            cliente.user = user
        if commit:
            cliente.save()
        return cliente