from django import forms
from django.contrib.auth.models import User
from .models import Cliente

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = '__all__'

class RegistroClienteForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Contraseña',
            'autocomplete': 'new-password',
            'type': 'password',
            'style': 'background:transparent;color:#fff;'
        })
    )
    nombre = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Nombre',
            'autocomplete': 'name',
            'type': 'text',
            'style': 'background:transparent;color:#fff;'
        })
    )
    correo = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'Correo',
            'autocomplete': 'email',
            'type': 'email',
            'style': 'background:transparent;color:#fff;'
        })
    )
    telefono = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Teléfono',
            'autocomplete': 'tel',
            'type': 'tel',
            'style': 'background:transparent;color:#fff;'
        })
    )

    class Meta:
        model = Cliente
        fields = ['nombre', 'correo', 'telefono']

    def save(self, commit=True):
        cliente = super().save(commit=False)
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