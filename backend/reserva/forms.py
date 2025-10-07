from django import forms
from .models import Reserva
from clientes.models import Cliente

class ReservaForm(forms.ModelForm):
    cliente = forms.ModelChoiceField(queryset=Cliente.objects.all(), required=True, label="Cliente")

    class Meta:
        model = Reserva
        fields = ['cliente', 'servicio', 'gestora', 'fecha', 'hora', 'estado']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-control'}),
            'servicio': forms.Select(attrs={'class': 'form-control'}),
            'gestora': forms.Select(attrs={'class': 'form-control'}),
            'fecha': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'placeholder': 'Selecciona la fecha'
            }),
            'hora': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control',
                'placeholder': 'Selecciona la hora'
            }),
            'estado': forms.Select(attrs={'class': 'form-control'}),
        }

class ReservaEditForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['cliente', 'servicio', 'gestora', 'fecha', 'hora', 'estado']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-control'}),
            'servicio': forms.Select(attrs={'class': 'form-control'}),
            'gestora': forms.Select(attrs={'class': 'form-control'}),
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'hora': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
        }