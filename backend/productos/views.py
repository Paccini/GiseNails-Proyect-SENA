from django.shortcuts import render
from .models import Producto
from django.core.paginator import Paginator
from django.views.decorators.http import require_GET

@require_GET
def lista_productos(request):
    productos_list = Producto.objects.all()
    paginator = Paginator(productos_list, 2)  # 2 productos por página
    page_number = request.GET.get('page')
    productos = paginator.get_page(page_number)
    return render(request, 'productos/lista_productos.html', {'productos': productos})

