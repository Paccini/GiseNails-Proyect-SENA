from django.db import models

from django.db import models

class Producto(models.Model):
	nombre = models.CharField(max_length=100)
	descripcion = models.TextField()
	imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
	destacado = models.BooleanField(default=False)
	precio = models.DecimalField(max_digits=10, decimal_places=2, default=0)

	def __str__(self):
		return self.nombre
