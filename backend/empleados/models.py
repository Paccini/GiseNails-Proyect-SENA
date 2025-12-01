from django.db import models

class Empleado(models.Model):
    nombre = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=150)
    correo = models.EmailField(unique=True)
    foto = models.ImageField(upload_to='empleados_fotos/', blank=True, null=True)
    activo = models.BooleanField(default=True, help_text="Si False el empleado está deshabilitado")
    reset_token = models.CharField(max_length=64, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} {self.apellidos}"