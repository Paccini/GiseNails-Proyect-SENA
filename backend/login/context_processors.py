from clientes.models import Cliente
from reserva.models import Reserva

def notificaciones_context(request):
    notificaciones = []
    if request.user.is_authenticated and request.user.is_staff:
        # Últimas 5 citas creadas
        for cita in Reserva.objects.order_by('-fecha')[:5]:
            notificaciones.append({
                'icon': 'bi-calendar-check',
                'texto': f'Cita creada para {cita.cliente}',
                'fecha': cita.fecha.strftime('%d/%m/%Y %H:%M')
            })
        # Últimos 5 clientes registrados
        for cliente in Cliente.objects.order_by('-id')[:5]:
            notificaciones.append({
                'icon': 'bi-person-plus',
                'texto': f'Cliente registrado: {cliente}',
                'fecha': cliente.fecha_registro.strftime('%d/%m/%Y %H:%M') if hasattr(cliente, 'fecha_registro') else ''
            })
    return {'notificaciones': notificaciones}