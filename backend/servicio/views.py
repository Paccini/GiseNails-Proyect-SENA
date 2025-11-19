from django.core.paginator import Paginator
from django.views.decorators.http import require_GET
from django.shortcuts import render, redirect, get_object_or_404
from .models import Servicio
from .forms import ServicioForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.cache import never_cache


@require_GET
def lista_servicios(request):
    servicios_list = Servicio.objects.all()
    paginator = Paginator(servicios_list, 3)  # 3 servicios por página
    page_number = request.GET.get('page')
    servicios = paginator.get_page(page_number)

    # Servicios más solicitados (placeholder: últimos agregados / top por id)
    mas_solicitados = Servicio.objects.all().order_by('-id')[:6]

    return render(request, 'servicios/lista_servicios.html', {
        'servicios': servicios,
        'mas_solicitados': mas_solicitados,
    })

# Create your views here.

@login_required
@user_passes_test(lambda u: u.is_staff)
@never_cache
def servicio_list(request):
    q = request.GET.get('q', '')
    servicios = Servicio.objects.all()
    if q:
        servicios = servicios.filter(nombre__icontains=q)
    paginator = Paginator(servicios, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'servicios/servicio_list.html', {
        'servicios': page_obj,
        'q': q,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
        'paginator': paginator,
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@never_cache
def servicio_create(request):
    if request.method == 'POST':
        form = ServicioForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('servicio:servicio_list')
    else:
        form = ServicioForm()
    return render(request, 'servicios/servicio_form.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_staff)
@never_cache
def servicio_update(request, pk):
    servicio = get_object_or_404(Servicio, pk=pk)
    if request.method == 'POST':
        form = ServicioForm(request.POST, request.FILES, instance=servicio)
        if form.is_valid():
            form.save()
            return redirect('servicio:servicio_list')
    else:
        form = ServicioForm(instance=servicio)
    return render(request, 'servicios/servicio_form.html', {'form': form, 'servicio': servicio})

@login_required
@user_passes_test(lambda u: u.is_staff)
@never_cache
def servicio_delete(request, pk):
    servicio = get_object_or_404(Servicio, pk=pk)
    if request.method == 'POST':
        servicio.delete()
        return redirect('servicio:servicio_list')
    return render(request, 'servicios/servicio_confirm_delete.html', {'servicio': servicio})

@login_required
@user_passes_test(lambda u: u.is_staff)
@never_cache
def servicio_detail(request, pk):
    servicio = get_object_or_404(Servicio, pk=pk)
    return render(request, 'servicios/servicio_detail.html', {'servicio': servicio})