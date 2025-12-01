from django.shortcuts import render, redirect, get_object_or_404
from .models import Empleado
from .forms import EmpleadoForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.cache import never_cache
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from reserva.models import Reserva, HorarioDisponible
from django import forms
from clientes.models import Cliente
from django.http import JsonResponse
from django.contrib import messages
from datetime import datetime


class EditarCitaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['fecha', 'hora', 'servicio', 'estado']


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
            empleado = form.save(commit=False)
            correo = form.cleaned_data.get('correo') or ''
            password = form.cleaned_data.get('password') or None
            user, created = User.objects.get_or_create(username=correo, defaults={'email': correo})
            if password:
                user.set_password(password)
                user.save()
            try:
                empleado.user = user
            except Exception:
                pass
            empleado.save()
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
            empleado = form.save(commit=False)
            correo = form.cleaned_data.get('correo') or ''
            password = form.cleaned_data.get('password') or None
            user = None
            try:
                user = empleado.user
            except Exception:
                user = None
            if user is None:
                user, created = User.objects.get_or_create(username=correo, defaults={'email': correo})
            else:
                if correo and user.username != correo:
                    user.username = correo
                    user.email = correo
            if password:
                user.set_password(password)
            user.save()
            try:
                empleado.user = user
            except Exception:
                pass
            empleado.save()
            return redirect('empleados:empleado_list')
    else:
        form = EmpleadoForm(instance=empleado)
    return render(request, 'empleados/empleado_form.html', {'form': form, 'empleado': empleado})


@login_required
@user_passes_test(lambda u: u.is_staff)
@never_cache
def empleado_delete(request, pk):
    """
    Ya no elimina el empleado. Alterna (habilita/deshabilita) el campo 'activo'.
    No permite deshabilitar si el empleado tiene reservas pendientes/confirmadas.
    """
    empleado = get_object_or_404(Empleado, pk=pk)
    if request.method == 'POST':
        # Si se intenta deshabilitar, comprobar reservas activas
        if empleado.activo:
            reservas_activas = Reserva.objects.filter(gestora=empleado, estado__in=['pendiente', 'confirmada']).exists()
            if reservas_activas:
                messages.error(request, "No se puede deshabilitar: el empleado tiene reservas pendientes o confirmadas.")
                return redirect('empleados:empleado_list')
        # Alternar activo
        empleado.activo = not empleado.activo
        empleado.save()
        estado = "habilitado" if empleado.activo else "deshabilitado"
        messages.success(request, f"Empleado {empleado.nombre} {empleado.apellidos} {estado}.")
        return redirect('empleados:empleado_list')
    # Mostrar confirmación (antes era confirm delete)
    return render(request, 'empleados/empleado_confirm_delete.html', {'empleado': empleado})


@login_required
@never_cache
def panel_empleado(request):
    from servicio.models import Servicio
    from clientes.models import Cliente
    empleado = get_object_or_404(Empleado, correo__iexact=request.user.email)

    # filtros
    estado = request.GET.get('estado', 'all')
    fecha_inicio = request.GET.get('fecha_inicio', '').strip()
    fecha_fin = request.GET.get('fecha_fin', '').strip()
    page = request.GET.get('page', 1)

    citas_qs = Reserva.objects.filter(gestora=empleado).order_by('-fecha', '-hora')

    if estado and estado != 'all':
        citas_qs = citas_qs.filter(estado=estado)

    # Filtrar por rango de fechas (siempre acepta ISO YYYY-MM-DD desde input date)
    if fecha_inicio:
        try:
            fecha_inicio_obj = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            citas_qs = citas_qs.filter(fecha__gte=fecha_inicio_obj)
        except Exception:
            pass
    if fecha_fin:
        try:
            fecha_fin_obj = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            citas_qs = citas_qs.filter(fecha__lte=fecha_fin_obj)
        except Exception:
            pass

    paginator = Paginator(citas_qs, 3)  # 3 por página (ajusta si quieres)
    citas_page = paginator.get_page(page)

    servicios = Servicio.objects.all()
    horas_disponibles = HorarioDisponible.objects.all()
    clientes = Cliente.objects.all()
    return render(request, 'empleados/panel_empleado', {
        'empleado': empleado,
        'citas': citas_page,
        'servicios': servicios,
        'horas_disponibles': horas_disponibles,
        'clientes': clientes,
        'filter_estado': estado,
        'filter_fecha_inicio': fecha_inicio,
        'filter_fecha_fin': fecha_fin,
    })


@login_required
@never_cache
def editar_cita_empleado(request, pk):
    from servicio.models import Servicio
    empleado = get_object_or_404(Empleado, correo__iexact=request.user.email)
    cita = get_object_or_404(Reserva, pk=pk, gestora=empleado)
    # Solo horas no ocupadas por otra reserva de la misma gestora y fecha, o la hora actual de la cita
    ocupadas = Reserva.objects.filter(
        gestora=empleado,
        fecha=cita.fecha
    ).exclude(pk=cita.pk).values_list('hora_id', flat=True)
    horas_disponibles = HorarioDisponible.objects.exclude(id__in=ocupadas) | HorarioDisponible.objects.filter(id=cita.hora_id)
    servicios = Servicio.objects.all()

    if request.method == 'POST':
        fecha = request.POST.get('fecha')
        hora_id = request.POST.get('hora')
        servicio_id = request.POST.get('servicio')
        estado = request.POST.get('estado')
        if fecha and hora_id and servicio_id and estado:
            cita.fecha = fecha
            cita.hora_id = hora_id
            cita.servicio_id = servicio_id
            cita.estado = estado
            cita.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            return redirect('empleados:panel_empleado')
    # Si GET, devuelve solo las horas disponibles para ese día y gestora
    return render(request, 'empleados/panel_empleado', {
        'empleado': empleado,
        'citas': Reserva.objects.filter(gestora=empleado),
        'servicios': servicios,
        'horas_disponibles': horas_disponibles.distinct(),
        'edit_cita': cita,
    })


@login_required
@never_cache
def horas_disponibles_empleado(request):
    fecha = request.GET.get('fecha')
    empleado = get_object_or_404(Empleado, correo__iexact=request.user.email)
    horarios = HorarioDisponible.objects.all()
    from datetime import datetime
    try:
        fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
    except Exception:
        return JsonResponse({'horarios': []})
    ocupados = Reserva.objects.filter(gestora=empleado, fecha=fecha_obj).values_list('hora_id', flat=True)
    disponibles = horarios.exclude(id__in=ocupados)
    data = [{'id': h.id, 'hora': h.hora.strftime('%H:%M')} for h in disponibles]
    return JsonResponse({'horarios': data})


@login_required
@never_cache
def agendar_cita_empleado(request):
    if request.method == 'POST':
        empleado = get_object_or_404(Empleado, correo__iexact=request.user.email)
        cliente_id = request.POST.get('cliente')
        fecha = request.POST.get('fecha')
        hora_id = request.POST.get('hora')
        servicio_id = request.POST.get('servicio')
        if not (cliente_id and fecha and hora_id and servicio_id):
            return JsonResponse({'success': False, 'error': 'Todos los campos son obligatorios.'})
        # Validar que la hora esté disponible
        existe = Reserva.objects.filter(
            gestora=empleado,
            fecha=fecha,
            hora_id=hora_id
        ).exists()
        if existe:
            return JsonResponse({'success': False, 'error': 'La hora seleccionada ya está ocupada.'})
        Reserva.objects.create(
            cliente_id=cliente_id,
            gestora=empleado,
            fecha=fecha,
            hora_id=hora_id,
            servicio_id=servicio_id,
            estado='pendiente'
        )
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Método no permitido.'})


def toggle_empleado_activo(request, pk):
    """
    Endpoint AJAX para alternar empleado.activo con validación de reservas.
    """
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'No autorizado.'}, status=403)

    empleado = get_object_or_404(Empleado, pk=pk)
    if empleado.activo:
        tiene_reservas = Reserva.objects.filter(gestora=empleado, estado__in=['pendiente', 'confirmada']).exists()
        if tiene_reservas:
            return JsonResponse({'success': False, 'error': 'El empleado tiene reservas pendientes o confirmadas.'})
    empleado.activo = not empleado.activo
    empleado.save()
    return JsonResponse({'success': True, 'activo': empleado.activo})



