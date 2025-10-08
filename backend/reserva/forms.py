from django import forms
from .models import Reserva
from clientes.models import Cliente
from reserva.models import HorarioDisponible

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
            'hora': forms.Select(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        # Recibe instancia y datos extra
        instance = kwargs.get('instance')
        super().__init__(*args, **kwargs)
        if instance:
            fecha = instance.fecha
            gestora = instance.gestora
            # Obtén las horas ocupadas para esa fecha y gestora, excluyendo la cita actual
            ocupadas = Reserva.objects.filter(
                gestora=gestora,
                fecha=fecha
            ).exclude(pk=instance.pk).values_list('hora_id', flat=True)
            # Solo muestra horas no ocupadas o la hora actual de la cita
            qs = HorarioDisponible.objects.exclude(id__in=ocupadas) | HorarioDisponible.objects.filter(id=instance.hora_id)
            self.fields['hora'].queryset = qs.distinct().order_by('hora')