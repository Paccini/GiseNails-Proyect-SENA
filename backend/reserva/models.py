from django.db import models
from empleados.models import Empleado
from servicio.models import Servicio
from productos.models import Producto
from clientes.models import Cliente

class HorarioDisponible(models.Model):
    hora = models.TimeField(unique=True)  # Ejemplo: 09:00, 10:00, etc.

    def __str__(self):
        return self.hora.strftime('%H:%M')

    @staticmethod
    def cargar_horarios_default():
        """
        Crea los horarios fijos de 9:00 a 18:00, excepto 12:00.
        Ejecuta esto una vez desde el shell de Django.
        """
        from datetime import time
        horas = [
            time(9, 0),
            time(10, 0),
            time(11, 0),
            time(13, 0),
            time(14, 0),
            time(15, 0),
            time(16, 0),
            time(17, 0),
            time(18, 0),
        ]
        for h in horas:
            HorarioDisponible.objects.get_or_create(hora=h)

class Reserva(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
        ('realizada', 'Realizada'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    gestora = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True)
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True, blank=True)
    hora = models.ForeignKey(HorarioDisponible, on_delete=models.CASCADE)
    fecha = models.DateField()
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='pendiente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reserva de {self.servicio.nombre} con {self.gestora.nombre} para {self.cliente} el {self.fecha} a las {self.hora}"

class PagoReserva(models.Model):
    reserva = models.ForeignKey('Reserva', on_delete=models.CASCADE, related_name='pagos')
    cliente = models.ForeignKey('clientes.Cliente', on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    metodo = models.CharField(max_length=20, choices=[('nequi', 'Nequi'), ('daviplata', 'Daviplata'), ('efectivo', 'Efectivo')])
    comprobante = models.ImageField(upload_to='comprobantes/', null=True, blank=True)
    fecha_pago = models.DateTimeField(auto_now_add=True)
    confirmado = models.BooleanField(default=False)
    referencia = models.CharField(max_length=30, blank=True, null=True)
    tipo_pago = models.CharField(max_length=15, choices=[('abono', 'Abono'), ('completo', 'Pago Completo'), ('saldo', 'Saldo Restante')], default='abono')

    def __str__(self):
        return f"{self.reserva} - {self.metodo} - {self.monto} - {self.tipo_pago}"

class Factura(models.Model):
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, related_name='facturas')
    cliente = models.ForeignKey('clientes.Cliente', on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    monto_total = models.DecimalField(max_digits=10, decimal_places=2)
    pagado = models.BooleanField(default=False)
    metodo = models.CharField(max_length=20, choices=[('nequi', 'Nequi'), ('daviplata', 'Daviplata'), ('efectivo', 'Efectivo')])
    referencia = models.CharField(max_length=30, blank=True, null=True)
    abono = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    saldo_restante = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Factura #{self.pk} - {self.cliente.nombre} - {self.monto_total}"
