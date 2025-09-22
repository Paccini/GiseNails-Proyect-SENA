from django.db import models

class Servicio(models.Model):
	nombre = models.CharField(max_length=100)
	descripcion = models.TextField()
	imagen = models.ImageField(upload_to='servicios/', blank=True, null=True)
	destacado = models.BooleanField(default=False)
	recomendaciones = models.TextField(blank=True, null=True)
	precio = models.DecimalField(max_digits=10, decimal_places=2, default=0)

	def __str__(self):
		return self.nombre

# Create your models here.
