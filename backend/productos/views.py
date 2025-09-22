
from django.shortcuts import render
from .models import Producto
from django.views.decorators.http import require_GET

@require_GET
def lista_productos(request):
	productos = Producto.objects.all()
	return render(request, 'productos/lista_productos.html', {'productos': productos})

@require_GET
def detalle_producto(request, id):
	from django.shortcuts import get_object_or_404
	producto = get_object_or_404(Producto, id=id)
	return render(request, 'productos/detalle_producto.html', {'producto': producto})
