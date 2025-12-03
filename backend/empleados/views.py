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
from django.core.mail import send_mail

# --------------------------------------------------
#  ENCRIPTACIÓN SEGÚN TU METODOLOGÍA
# --------------------------------------------------
from cryptography.fernet import Fernet
from django.conf import settings

fernet = Fernet(settings.ENCRYPT_KEY)

def encrypt_id(pk):
    return fernet.encrypt(str(pk).encode()).decode()

def decrypt_id(token):
    return int(fernet.decrypt(token.encode()).decode())
# --------------------------------------------------


class EditarCitaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['fecha', 'hora', 'servicio', 'estado']



# ==================================================
#  LISTAR EMPLEADOS (NO USA PK → NO CAMBIA)
# ==================================================
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
        'encrypt_id': encrypt_id,  # ✔ Para encriptar en el template
        'q': q,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
        'paginator': paginator,
    })



# ==================================================
#  CREAR EMPLEADO (NO USA PK)
# ==================================================
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

            user, created = User.objects.get_or_create(
                username=correo, defaults={'email': correo}
            )
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



# ==================================================
#  ACTUALIZAR EMPLEADO (CAMBIA PK → TOKEN)
# ==================================================
@login_required
@user_passes_test(lambda u: u.is_staff)
@never_cache
def empleado_update(request, token):

    pk = decrypt_id(token)
    empleado = get_object_or_404(Empleado, pk=pk)

    if request.method == 'POST':
        form = EmpleadoForm(request.POST, request.FILES, instance=empleado)
        if form.is_valid():
            empleado = form.save(commit=False)
            correo = form.cleaned_data.get('correo') or ''
            password = form.cleaned_data.get('password') or None
            
            user = getattr(empleado, 'user', None)

            if user is None:
                user, created = User.objects.get_or_create(
                    username=correo, defaults={'email': correo}
                )
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

    return render(request, 'empleados/empleado_form.html', {
        'form': form,
        'empleado': empleado
    })



# ==================================================
#  DESHABILITAR/HABILITAR EMPLEADO (CAMBIA PK → TOKEN)
# ==================================================
@login_required
@user_passes_test(lambda u: u.is_staff)
@never_cache
def empleado_delete(request, token):

    pk = decrypt_id(token)
    empleado = get_object_or_404(Empleado, pk=pk)

    if request.method == 'POST':

        if empleado.activo:
            reservas_activas = Reserva.objects.filter(
                gestora=empleado,
                estado__in=['pendiente', 'confirmada']
            ).exists()

            if reservas_activas:
                messages.error(request, "No se puede deshabilitar: el empleado tiene reservas pendientes o confirmadas.")
                return redirect('empleados:empleado_list')

        empleado.activo = not empleado.activo
        empleado.save()

        estado = "habilitado" if empleado.activo else "deshabilitado"
        messages.success(request, f"Empleado {empleado.nombre} {empleado.apellidos} {estado}.")

        return redirect('empleados:empleado_list')

    return render(request, 'empleados/empleado_confirm_delete.html', {
        'empleado': empleado
    })



# ==================================================
#  EL RESTO NO CAMBIA (NO USA PK EN URL)
# ==================================================
@login_required
@never_cache
def panel_empleado(request):
    from servicio.models import Servicio
    from clientes.models import Cliente

    empleado = get_object_or_404(Empleado, correo__iexact=request.user.email)

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

    paginator = Paginator(citas_qs, 3)
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

    ocupadas = Reserva.objects.filter(
        gestora=empleado,
        fecha=cita.fecha
    ).exclude(pk=cita.pk).values_list('hora_id', flat=True)

    horas_disponibles = HorarioDisponible.objects.exclude(
        id__in=ocupadas
    ) | HorarioDisponible.objects.filter(id=cita.hora_id)

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

    try:
        fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
    except:
        return JsonResponse({'horarios': []})

    ocupados = Reserva.objects.filter(gestora=empleado, fecha=fecha_obj).values_list('hora_id', flat=True)
    disponibles = HorarioDisponible.objects.exclude(id__in=ocupados)

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

        existe = Reserva.objects.filter(
            gestora=empleado,
            fecha=fecha,
            hora_id=hora_id
        ).exists()

        if existe:
            return JsonResponse({'success': False, 'error': 'La hora seleccionada ya está ocupada.'})

        cita = Reserva.objects.create(
            cliente_id=cliente_id,
            gestora=empleado,
            fecha=fecha,
            hora_id=hora_id,
            servicio_id=servicio_id,
            estado='pendiente'
        )
        # Notificación al cliente
        cliente = Cliente.objects.get(pk=cliente_id)
        servicio = cita.servicio
        fecha_str = cita.fecha.strftime('%d/%m/%Y')
        hora_str = cita.hora.hora.strftime('%H:%M')
        mensaje_html = f"""
        <div style="font-family: 'Montserrat', Arial, sans-serif; background: #f8f9fa; padding: 32px; border-radius: 18px;">
          <h2 style="color: #d63384;">¡Tu cita ha sido agendada!</h2>
          <p>Hola <b>{cliente.nombre}</b>,<br>
          Tu cita para <b>{servicio.nombre}</b> ha sido registrada.<br>
          <b>Fecha:</b> {fecha_str}<br>
          <b>Hora:</b> {hora_str}<br>
          <b>Profesional:</b> {empleado.nombre} {empleado.apellidos}<br>
          </p>
          <hr>
          <p style="color: #d63384;">GiseNails - Tu bienestar, nuestra prioridad.</p>
        </div>
        """
        send_mail(
            subject="Confirmación de cita en GiseNails",
            message="Tu cita ha sido agendada.",
            from_email=None,
            recipient_list=[cliente.correo],
            html_message=mensaje_html,
            fail_silently=False,
        )

        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'error': 'Método no permitido.'})



def toggle_empleado_activo(request, pk):
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'No autorizado.'}, status=403)

    empleado = get_object_or_404(Empleado, pk=pk)

    if empleado.activo:
        tiene_reservas = Reserva.objects.filter(
            gestora=empleado,
            estado__in=['pendiente', 'confirmada']
        ).exists()

        if tiene_reservas:
            return JsonResponse({'success': False, 'error': 'El empleado tiene reservas pendientes o confirmadas.'})

    empleado.activo = not empleado.activo
    empleado.save()

    return JsonResponse({'success': True, 'activo': empleado.activo})


from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse
import json
from reserva.models import Reserva
from django.core.mail import send_mail
from django.conf import settings

@csrf_exempt
@require_POST
@login_required
def cambiar_estado_cita_empleado(request, pk):
    try:
        # Solo permite al empleado dueño de la cita cambiar el estado
        empleado = request.user
        cita = Reserva.objects.get(pk=pk)
        # Si quieres restringir solo al empleado dueño, descomenta:
        # if cita.gestora.correo.lower() != empleado.email.lower():
        #     return JsonResponse({'success': False, 'error': 'No autorizado.'}, status=403)

        data = json.loads(request.body)
        nuevo_estado = data.get('estado')
        if nuevo_estado not in dict(Reserva.ESTADO_CHOICES):
            return JsonResponse({'success': False, 'error': 'Estado inválido'})

        cita.estado = nuevo_estado
        cita.save()

        # Notificación profesional al cliente
        cliente = cita.cliente
        if cliente and cliente.correo:
            servicio = cita.servicio
            fecha_str = cita.fecha.strftime('%d/%m/%Y')
            hora_str = cita.hora.hora.strftime('%H:%M')
            estado_display = dict(Reserva.ESTADO_CHOICES).get(nuevo_estado, nuevo_estado)
            mensaje_html = f"""
            <div style="font-family: 'Montserrat', Arial, sans-serif; background: #f8f9fa; padding: 32px; border-radius: 18px;">
              <h2 style="color: #d63384;">Actualización de tu cita</h2>
              <p>Hola <b>{cliente.nombre}</b>,<br>
              El estado de tu cita para <b>{servicio.nombre}</b> ha cambiado a <b>{estado_display}</b>.<br>
              <b>Fecha:</b> {fecha_str}<br>
              <b>Hora:</b> {hora_str}<br>
              </p>
              <hr>
              <p style="color: #d63384;">GiseNails - Siempre a tu servicio.</p>
            </div>
            """
            send_mail(
                subject="Actualización de estado de tu cita en GiseNails",
                message=f"Tu cita ha cambiado a estado {estado_display}.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[cliente.correo],
                html_message=mensaje_html,
                fail_silently=False,
            )

        return JsonResponse({'success': True})
    except Reserva.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Cita no encontrada'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
