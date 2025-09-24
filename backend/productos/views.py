
from django.shortcuts import render
from .models import Producto
from django.views.decorators.http import require_GET

@require_GET
def lista_productos(request):
	productos = Producto.objects.all()
	return render(request, 'productos/lista_productos.html', {'productos': productos})

