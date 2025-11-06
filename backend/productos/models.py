from django.db import models

class Producto(models.Model):
	nombre = models.CharField(max_length=100)
	descripcion = models.TextField()
	imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
	cantidad = models.PositiveIntegerField(default=0)  # Nuevo campo
	precio = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	recomendado = models.BooleanField(default=False, help_text="Marcar como recomendado / más vendido")
	en_uso = models.BooleanField(default=False, help_text="Marcar si se usa en el estudio / experiencia")
	ventas = models.PositiveIntegerField(default=0, help_text="Contador sencillo de ventas")

	def __str__(self):
		return self.nombre
