from django.db import models

class Empleado(models.Model):
    nombre = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100, default="Sin apellidos")
    correo = models.EmailField(unique=True)
    fotos = models.ImageField(upload_to='empleados/', blank=True, null=True)

    class Meta:
        db_table = 'empleados_empleado'  # Para usar la tabla existente

    def __str__(self):
        return f"{self.nombre} {self.apellidos}"
