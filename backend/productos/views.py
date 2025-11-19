from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto
from .forms import ProductoForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.cache import never_cache
from django.core.paginator import Paginator
from django.views.decorators.http import require_GET

@login_required
@user_passes_test(lambda u: u.is_staff)
@never_cache
def producto_list(request):
    q = request.GET.get('q', '')
    productos = Producto.objects.all()
    if q:
        productos = productos.filter(nombre__icontains=q)
    paginator = Paginator(productos, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'productos/producto_list.html', {
        'productos': page_obj,
        'q': q,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
        'paginator': paginator,
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@never_cache
def producto_create(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('producto:producto_list')
    else:
        form = ProductoForm()
    return render(request, 'productos/producto_form.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_staff)
@never_cache
def producto_update(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('producto:producto_list')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'productos/producto_form.html', {'form': form, 'producto': producto})

@login_required
@user_passes_test(lambda u: u.is_staff)
@never_cache
def producto_delete(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.delete()
        return redirect('producto:producto_list')
    return render(request, 'productos/producto_confirm_delete.html', {'producto': producto})

def producto_detail(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    return render(request, 'productos/producto_detail.html', {'producto': producto})

@require_GET
def lista_productos(request):
    productos_list = Producto.objects.all()
    paginator = Paginator(productos_list, 3)  # 4 productos por página
    page_number = request.GET.get('page')
    productos = paginator.get_page(page_number)

    recomendados = Producto.objects.filter(recomendado=True).order_by('-ventas')[:6]
    en_uso = Producto.objects.filter(en_uso=True)[:6]

    # DEBUG temporal -> revisa la consola donde corre runserver
    print("DEBUG lista_productos: recomendados=", recomendados.count(), " en_uso=", en_uso.count())

    return render(request, 'productos/lista_productos.html', {
        'productos': productos,
        'recomendados': recomendados,
        'en_uso': en_uso,
    })