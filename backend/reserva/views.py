from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from empleados.models import Empleado
from servicio.models import Servicio
from clientes.models import Cliente
from .forms import ReservaForm, ReservaEditForm
from reserva.models import HorarioDisponible, Reserva
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.cache import never_cache
from django.core.paginator import Paginator
from django.utils import timezone
from productos.models import Producto
from django.db.models import Count
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Reserva
from datetime import datetime, time

def reserva(request):
    gestoras = Empleado.objects.all()
    horarios = HorarioDisponible.objects.all()
    servicios = Servicio.objects.all()
    # Agrupa servicios por categoría
    servicios_por_categoria = {
        'manicure': servicios.filter(categoria='manicure'),
        'pedicure': servicios.filter(categoria='pedicure'),
        'estructura': servicios.filter(categoria='estructura'),
    }

    if request.method == "POST":
        try:
            gestora_id = request.POST.get("gestora")
            nombre_cliente = request.POST.get("nombre")
            telefono_cliente = request.POST.get("telefono")
            servicio_id = request.POST.get("servicio")
            hora_id = request.POST.get("hora")
            fecha_str = request.POST.get("fecha")
            correo_cliente = request.POST.get("correo")

            # Validaciones básicas: asegurar que los ids existen
            if not gestora_id or not servicio_id or not hora_id:
                return JsonResponse({"success": False, "error": "Selecciona gestora, servicio y horario."})

            try:
                gestora = Empleado.objects.get(id=gestora_id)
            except Empleado.DoesNotExist:
                return JsonResponse({"success": False, "error": "Gestora no encontrada."})

            try:
                servicio = Servicio.objects.get(id=servicio_id)
            except Servicio.DoesNotExist:
                return JsonResponse({"success": False, "error": "Servicio no encontrado."})

            try:
                hora = HorarioDisponible.objects.get(id=hora_id)
            except HorarioDisponible.DoesNotExist:
                return JsonResponse({"success": False, "error": "Horario no disponible (selecciona otro)."})

            # parsear fecha (se espera formato d/m/Y desde flatpickr)
            from datetime import datetime
            try:
                fecha = datetime.strptime(fecha_str, '%d/%m/%Y').date()
            except Exception:
                # intentar ISO (Y-m-d)
                fecha = datetime.fromisoformat(fecha_str).date()

            # Preparar datos de reserva para guardarlos en sesión y completar tras login/registro
            pending = {
                'gestora_id': gestora.id,
                'servicio_id': servicio.id,
                'hora_id': hora.id,
                'fecha': fecha.strftime('%Y-%m-%d'),
                'nombre': nombre_cliente,
                'telefono': telefono_cliente,
                'correo': correo_cliente,
            }

            # comprobar si el correo ya existe en clientes
            from clientes.models import Cliente
            cliente_obj = Cliente.objects.filter(correo__iexact=correo_cliente).first()
            request.session['pending_reserva'] = pending

            if cliente_obj:
                # ya existe: pedir login (solo contraseña)
                from django.urls import reverse
                login_url = reverse('login:login')
                return JsonResponse({"next": f"{login_url}?next=/completar-reserva/", "need": "login"})
            else:
                # no existe: redirigir a registro
                from django.urls import reverse
                registro_url = reverse('clientes:registro')
                return JsonResponse({"next": f"{registro_url}?next=/completar-reserva/", "need": "register"})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return render(request, 'reservas/reserva.html', {
        'gestoras': gestoras,
        'horarios': horarios,
        'servicios_por_categoria': servicios_por_categoria,
    })

def horarios_disponibles(request):
    gestora_id = request.GET.get('gestora_id')
    fecha = request.GET.get('fecha')
    horarios = HorarioDisponible.objects.all()
    # parsear fecha entrante (d/m/Y)
    from datetime import datetime
    try:
        fecha_obj = datetime.strptime(fecha, '%d/%m/%Y').date()
    except Exception:
        try:
            fecha_obj = datetime.fromisoformat(fecha).date()
        except Exception:
            return JsonResponse({'horarios': []})

    ocupados = Reserva.objects.filter(gestora_id=gestora_id, fecha=fecha_obj).values_list('hora_id', flat=True)
    disponibles = horarios.exclude(id__in=ocupados)
    # devolver id y texto para cada horario
    data = [{'id': h.id, 'hora': h.hora.strftime('%H:%M')} for h in disponibles]
    return JsonResponse({'horarios': data})

@login_required
@user_passes_test(lambda u: u.is_staff)
@never_cache
def home(request):
    ahora = timezone.localtime()
    hoy = ahora.date()
    hora_actual = ahora.time().replace(second=0, microsecond=0)

    # Cancelar solo las pendientes cuya fecha es menor a hoy
    Reserva.objects.filter(
        estado='pendiente',
        fecha__lt=hoy
    ).update(estado='cancelada')

    # Cancelar solo las pendientes de hoy cuya hora ya pasó
    Reserva.objects.filter(
        estado='pendiente',
        fecha=hoy,
        hora__hora__lt=hora_actual
    ).update(estado='cancelada')

    fecha = request.GET.get('fecha', '')
    usuario = request.GET.get('usuario', '')
    estado = request.GET.get('estado', '')

    citas = Reserva.objects.all()
    # Excluye canceladas y realizadas por defecto
    if not estado:
        citas = citas.exclude(estado__in=['realizada', 'cancelada'])
    else:
        citas = citas.filter(estado=estado)

    if fecha:
        citas = citas.filter(fecha=fecha)
    if usuario:
        citas = citas.filter(cliente__nombre__icontains=usuario)

    citas = citas.order_by('fecha', 'hora__hora')

    paginator = Paginator(citas, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'reservas': page_obj,
        'fecha': fecha,
        'usuario': usuario,
        'estado': estado,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
        'paginator': paginator,
    }
    return render(request, 'reservas/home.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
@never_cache
def agregar_reserva(request):
    fecha = request.GET.get('fecha')
    gestora = request.GET.get('gestora')
    form = ReservaForm(request.POST or None)

    # Filtra las horas solo si hay fecha y gestora seleccionadas
    if fecha and gestora:
        ocupadas = Reserva.objects.filter(
            gestora_id=gestora,
            fecha=fecha
        ).values_list('hora_id', flat=True)
        horas_disponibles = HorarioDisponible.objects.exclude(id__in=ocupadas)
        form.fields['hora'].queryset = horas_disponibles.order_by('hora')
    else:
        form.fields['hora'].queryset = HorarioDisponible.objects.all().order_by('hora')

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('reserva:home')

    return render(request, 'reservas/agregar.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_staff)
@never_cache
def editar_reserva(request, pk):
    cita = get_object_or_404(Reserva, pk=pk)
    if request.method == 'POST':
        form = ReservaEditForm(request.POST, instance=cita)
        if form.is_valid():
            form.save()
            return redirect('reserva:home')
    else:
        form = ReservaEditForm(instance=cita)
    context = {'form': form}
    return render(request, 'reservas/editar.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
@never_cache
def eliminar_reserva(request, pk):
    cita = get_object_or_404(Reserva, pk=pk)
    if request.method == 'POST':
        cita.delete()
        return redirect("reserva:home")
    return render(request, 'reservas/eliminar.html', {'cita': cita})


class ReservaCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Reserva
    form_class = ReservaForm
    template_name = 'reservas/agregar.html'
    success_url = reverse_lazy('reserva:home')

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        # El formulario ya tiene el cliente seleccionado
        self.object = form.save()
        return super().form_valid(form)

from django.contrib.auth.decorators import login_required

@login_required
def completar_reserva(request):
    pending = request.session.get('pending_reserva')
    if not pending:
        return redirect('clientes:panel')  # Si no hay reserva pendiente, muestra el panel

    # Obtén el cliente autenticado
    from clientes.models import Cliente
    cliente = Cliente.objects.filter(user=request.user).first()
    if not cliente:
        return redirect('clientes:registro')

    # Solo crea la reserva si no existe ya para ese horario y fecha
    from reserva.models import Reserva, HorarioDisponible
    from empleados.models import Empleado
    from servicio.models import Servicio

    existe = Reserva.objects.filter(
        cliente=cliente,
        gestora_id=pending['gestora_id'],
        servicio_id=pending['servicio_id'],
        hora_id=pending['hora_id'],
        fecha=pending['fecha']
    ).exists()

    if not existe:
        Reserva.objects.create(
            cliente=cliente,
            gestora=Empleado.objects.get(id=pending['gestora_id']),
            servicio=Servicio.objects.get(id=pending['servicio_id']),
            hora=HorarioDisponible.objects.get(id=pending['hora_id']),
            fecha=pending['fecha'],
            estado='pendiente'
        )

    # Limpia la sesión
    del request.session['pending_reserva']

    # Redirige al panel del cliente
    return redirect('clientes:panel')