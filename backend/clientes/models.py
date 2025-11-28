from django.db import models
from django.contrib.auth.models import User

class Cliente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    nombre = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True, help_text="Si False el cliente está deshabilitado")
    reset_token = models.CharField(max_length=64, blank=True, null=True)

    def __str__(self):
        return self.nombre


