from django.db import models

class Servicio(models.Model):
    CATEGORIA_CHOICES = [
        ('manicure', 'Manicure'),
        ('pedicure', 'Pedicure'),
        ('estructura', 'Estructura'),

    ]

    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    descripcion = models.TextField(blank=True)
    imagen = models.ImageField(upload_to='servicios/', blank=True, null=True)
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)

    def __str__(self):
        return self.nombre

# Create your models here.
