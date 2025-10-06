from django.shortcuts import render, redirect, get_object_or_404
from .models import Empleado
from .forms import EmpleadoForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.cache import never_cache
from django.core.paginator import Paginator

@login_required
@user_passes_test(lambda u: u.is_staff)
@never_cache
def empleado_list(request):
    q = request.GET.get('q', '')
    empleados = Empleado.objects.all()
    if q:
        empleados = empleados.filter(nombre__icontains=q)
    paginator = Paginator(empleados, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'empleados/empleado_list.html', {
        'empleados': page_obj,
        'q': q,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
        'paginator': paginator,
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@never_cache
def empleado_create(request):
    if request.method == 'POST':
        form = EmpleadoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('empleados:empleado_list')
    else:
        form = EmpleadoForm()
    return render(request, 'empleados/empleado_form.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_staff)
@never_cache
def empleado_update(request, pk):
    empleado = get_object_or_404(Empleado, pk=pk)
    if request.method == 'POST':
        form = EmpleadoForm(request.POST, request.FILES, instance=empleado)
        if form.is_valid():
            form.save()
            return redirect('empleados:empleado_list')
    else:
        form = EmpleadoForm(instance=empleado)
    return render(request, 'empleados/empleado_form.html', {'form': form, 'empleado': empleado})

@login_required
@user_passes_test(lambda u: u.is_staff)
@never_cache
def empleado_delete(request, pk):
    empleado = get_object_or_404(Empleado, pk=pk)
    if request.method == 'POST':
        empleado.delete()
        return redirect('empleados:empleado_list')
    return render(request, 'empleados/empleado_confirm_delete.html', {'empleado': empleado})