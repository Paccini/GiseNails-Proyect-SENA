from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from clientes.models import Cliente
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required, user_passes_test
from productos.models import Producto
from servicio.models import Servicio
from reserva.models import Reserva
from django.utils import timezone
from django.db.models import Count, Sum, F, Case, When, DecimalField, Value
from django.db.models.functions import TruncDay
from django.http import HttpResponse
from .forms import UpdateUserForm
from empleados.models import Empleado
from clientes.forms import RegistroClienteForm
from django.utils.dateparse import parse_date
import datetime
from django.contrib import messages


# =============================
# LOGIN
# =============================
def login_view(request):
    error = None
    prefill_email = None
    password_only = False
    register_active = request.GET.get('register_active') == 'true'
    pending_message = bool(request.session.get('pending_reserva'))

    if request.method == 'POST':
        email = request.POST.get('username')
        password = request.POST.get('password')

        user_qs = User.objects.filter(email__iexact=email)
        user = user_qs.first()
        username = email if user is None else user.username

        user = authenticate(request, username=username, password=password)

        if user is not None:

            # Validación cliente inactivo
            cliente_obj = Cliente.objects.filter(user=user).first()
            if cliente_obj is not None and not cliente_obj.activo:
                error = "Tu cuenta está inactiva, contáctate con el administrador."
                logout(request)
                return render(request, 'login/login.html', {
                    'form': {}, 'error': error,
                    'prefill_email': None, 'password_only': False
                })

            # Validación empleado inactivo
            empleado_obj = Empleado.objects.filter(correo__iexact=user.email).first()
            if empleado_obj is not None and not empleado_obj.activo:
                error = "Tu cuenta está inactiva, contáctate con el administrador."
                logout(request)
                return render(request, 'login/login.html', {
                    'form': {}, 'error': error,
                    'prefill_email': None, 'password_only': False
                })

            # Inicio de sesión
            login(request, user)

            if cliente_obj:
                if request.session.get('pending_reserva'):
                    return redirect('/reserva/completar-reserva/')
                request.session['show_cita_alert'] = True
                return redirect('clientes:panel')

            if Empleado.objects.filter(correo__iexact=user.email).exists():
                return redirect('empleados:panel_empleado')

            if user.is_staff or user.is_superuser:
                return redirect('login:dashboard')

            error = "No tienes permisos para acceder."
        else:
            error = "Usuario o contraseña incorrectos."


    if request.session.get('pending_reserva'):
        pending = request.session.get('pending_reserva')
        prefill_email = pending.get('correo')
        password_only = True

    # Si viene register_active, mostrar el registro
    if register_active:
        from clientes.forms import RegistroClienteForm
        initial = {
            'nombre': pending.get('nombre', '') if pending else '',
            'correo': pending.get('correo', '') if pending else '',
            'telefono': pending.get('telefono', '') if pending else '',
        }
        form = RegistroClienteForm(initial=initial)
        return render(request, 'login/login.html', {
            'register_form': form,
            'register_active': True,
            'pending_message': pending_message,
            'initial': initial,
            'prefill_email': initial.get('correo'),
        })

    return render(request, 'login/login.html', {
        'form': {},
        'error': error,
        'prefill_email': prefill_email,
        'password_only': password_only,
        'pending_message': pending_message,
    })


# =============================
# REGISTRO CLIENTE
# =============================
def registro_cliente(request):
    pending = request.session.get('pending_reserva', {})
    initial = {
        'nombre': pending.get('nombre', ''),
        'correo': pending.get('correo', ''),
        'telefono': pending.get('telefono', ''),
    } if pending else {}

    if request.method == 'POST':
        form = RegistroClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save()
            user = getattr(cliente, 'user', None)

            if user:
                login(request, user)

            if request.session.get('pending_reserva'):
                return redirect('reserva:completar_reserva')

            return redirect('clientes:panel')
        else:
            # Mostrar alerta si el formulario no es válido
            messages.error(request, 'Por favor, verifica los datos ingresados. Asegúrate de que el correo sea válido y el número de teléfono tenga exactamente 10 dígitos.')

    else:
        form = RegistroClienteForm(initial=initial)

    # Borrar la cita pendiente si se cambia de vista
    if request.session.get('pending_reserva'):
        del request.session['pending_reserva']

    return render(request, 'login/login.html', {
        'register_form': form,
        'register_active': True,
        'pending_message': bool(pending),
        'initial': initial,
        'prefill_email': initial.get('correo')
    })


# =============================
# PANEL ADMIN
# =============================
@never_cache
@login_required(login_url='login:login')
def admin_panel(request):
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect('login:login')
    return redirect('login:dashboard')


# =============================
# LOGOUT
# =============================
def logout_view(request):
    logout(request)
    return redirect('login:login')


# =============================
# DASHBOARD (VERSIÓN FINAL TUYA)
# =============================
@login_required
@user_passes_test(lambda u: u.is_staff)
@never_cache
def dashboard(request):

    # Datos generales
    clientes_count = Cliente.objects.count()
    servicios_count = Servicio.objects.count()
    productos_count = Producto.objects.count()

    # Filtros
    inicio = request.GET.get('inicio')
    fin = request.GET.get('fin')

    ventas_total = 0
    meses = []
    datos_citas = []

    # filtrar solo realizadas
    qs = Reserva.objects.filter(estado="realizada")

    if inicio and fin:
        # parsear fechas y validar
        start_date = parse_date(inicio)
        end_date = parse_date(fin)
        if not start_date or not end_date or start_date > end_date:
            # rangos inválidos -> no mostrar nada
            start_date = None
            end_date = None

    else:
        start_date = None
        end_date = None

    if start_date and end_date:
        # filtrar por fecha (fecha es DateField -> usar rango directo sobre fecha)
        qs_range = qs.filter(fecha__range=(start_date, end_date)).select_related('producto', 'servicio')

        # Recorrer todas las reservas del rango y sumar en Python por fecha.
        # Esto evita problemas de joins/lookup y garantiza que si hay 2+ realizadas
        # en la misma fecha se sumen todas.
        totals_by_date = {}
        for r in qs_range:
            # obtener la fecha (si fecha es datetime -> date())
            d = r.fecha.date() if isinstance(r.fecha, datetime.datetime) else r.fecha
            # obtener precio desde producto o servicio (protegiendo nulos)
            precio = 0
            try:
                if getattr(r, 'producto', None):
                    precio = float(getattr(r.producto, 'precio', 0) or 0)
                elif getattr(r, 'servicio', None):
                    precio = float(getattr(r.servicio, 'precio', 0) or 0)
            except Exception:
                precio = 0
            totals_by_date[d] = totals_by_date.get(d, 0) + precio

        # construir lista completa de días entre start_date and end_date (incl.)
        days = []
        cur = start_date
        while cur <= end_date:
            days.append(cur)
            cur = cur + datetime.timedelta(days=1)

        meses = [d.strftime("%d/%m/%Y") for d in days]
        datos_citas = [totals_by_date.get(d, 0) for d in days]
        ventas_total = sum(datos_citas)

    # si no hay filtro válido: meses=[], datos_citas=[], ventas_total=0

    context = {
        'clientes_count': clientes_count,
        'servicios_count': servicios_count,
        'productos_count': productos_count,

        'ventas_total': ventas_total,
        'inicio': inicio,
        'fin': fin,

        'meses': meses,
        'datos_citas': datos_citas
    }

    return render(request, 'dashboard.html', context)


# =============================
# UPDATE USER
# =============================
@login_required(login_url='login:login')
def update_user(request):
    update_error = None
    update_success = None
    show_modal = False

    if request.method == 'POST':
        form = UpdateUserForm(request.POST)
        show_modal = True

        if form.is_valid():
            nombre = form.cleaned_data['nombre']
            old_password = form.cleaned_data['old_password']
            new_password = form.cleaned_data['new_password']
            user = request.user

            if not user.check_password(old_password):
                update_error = "La contraseña actual es incorrecta. No se realizaron cambios."
            else:
                nombre_parts = nombre.strip().split(' ', 1)
                user.first_name = nombre_parts[0]
                user.last_name = nombre_parts[1] if len(nombre_parts) > 1 else ''
                nuevo_username = nombre.replace(" ", "").lower()

                if User.objects.exclude(pk=user.pk).filter(username=nuevo_username).exists():
                    update_error = "El nombre de usuario ya está en uso. Elige otro nombre."
                else:
                    user.username = nuevo_username
                    if new_password:
                        user.set_password(new_password)
                    user.save()

                    if new_password:
                        from django.contrib.auth import update_session_auth_hash
                        update_session_auth_hash(request, user)

                    update_success = "¡Datos actualizados correctamente!"
                    show_modal = True

        return render(request, 'dashboard.html', {
            'form': form,
            'update_error': update_error,
            'update_success': update_success,
            'show_modal': show_modal,
        })

    else:
        form = UpdateUserForm(initial={'nombre': request.user.get_full_name()})

    return render(request, 'dashboard.html', {
        'form': form,
        'update_error': update_error,
        'update_success': None,
        'show_modal': show_modal,
    })
