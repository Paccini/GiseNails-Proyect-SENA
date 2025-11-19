from django import forms
from .models import Empleado

class EmpleadoForm(forms.ModelForm):
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(render_value=False),
        required=False,
        help_text='Dejar en blanco para no cambiar la contraseña.'
    )
    password_confirm = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(render_value=False),
        required=False
    )

    class Meta:
        model = Empleado
        fields = ['nombre', 'apellidos', 'correo', 'foto']  # ...existing code...

    def clean(self):
        cleaned = super().clean()
        p = cleaned.get('password')
        pc = cleaned.get('password_confirm')
        if p or pc:
            if p != pc:
                raise forms.ValidationError("Las contraseñas no coinciden.")
            if len(p) < 6:
                raise forms.ValidationError("La contraseña debe tener al menos 6 caracteres.")
        return cleaned