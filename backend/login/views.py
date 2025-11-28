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
from .forms import UpdateUserForm, LoginForm, PasswordResetForm, SetNewPasswordForm
from empleados.models import Empleado
from clientes.forms import RegistroClienteForm
from django.utils.dateparse import parse_date
import datetime
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.utils.crypto import get_random_string


# =============================
# LOGIN
# =============================
def login_view(request):
    error = None
    prefill_email = None
    password_only = False
    register_active = request.GET.get('register_active') == 'true'
    show_reset_form = request.GET.get('show_reset') == 'true'
    pending_message = bool(request.session.get('pending_reserva'))

    login_form = LoginForm()
    reset_form = PasswordResetForm()
    reset_success = None
    reset_error = None

    if request.method == 'POST':
        if 'reset_password' in request.POST:
            reset_form = PasswordResetForm(request.POST)
            if reset_form.is_valid():
                email = reset_form.cleaned_data['email']
                user = User.objects.filter(email__iexact=email).first()
                if user:
                    token = get_random_string(32)
                    cliente = Cliente.objects.filter(user=user).first()
                    if cliente:
                        cliente.reset_token = token
                        cliente.save()
                    else:
                        empleado = Empleado.objects.filter(correo__iexact=email).first()
                        if empleado:
                            empleado.reset_token = token
                            empleado.save()
                    reset_url = request.build_absolute_uri(
                        reverse('login:password_reset_confirm', args=[token])
                    )
                    send_mail(
                        'Restablecer contraseña',
                        f'Para restablecer tu contraseña haz clic aquí: {reset_url}',
                        settings.DEFAULT_FROM_EMAIL,
                        [email],
                        fail_silently=False,
                    )
                    reset_success = "Te hemos enviado un correo para restablecer tu contraseña."
                else:
                    reset_error = "El correo no está registrado."
            show_reset_form = True
        else:
            # Login normal
            email = request.POST.get('email')
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

                # Validación empleado inactiva
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

                # Adding debug messages to identify the failing condition during login redirection
                print(f"Debug: Cliente: {cliente_obj}, Empleado: {Empleado.objects.filter(correo__iexact=user.email).exists()}, Admin: {user.is_staff or user.is_superuser}")

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
                print("Debug: No matching role found for user.")
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

    context = {
        'form': login_form,
        'error': error,
        'prefill_email': prefill_email,
        'password_only': password_only,
        'pending_message': pending_message,
        'register_active': register_active,
        'show_reset_form': show_reset_form,
        'reset_form': reset_form,
        'reset_success': reset_success,
        'reset_error': reset_error,
    }
    return render(request, 'login/login.html', context)


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


# =============================
# RESTABLECER CONTRASEÑA
# =============================
def password_reset_view(request):
    success = None
    error = None
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.filter(email__iexact=email).first()
            if user:
                token = get_random_string(32)
                # Asume que tienes un campo reset_token en el modelo Cliente y/o Empleado
                cliente = Cliente.objects.filter(user=user).first()
                if cliente:
                    cliente.reset_token = token
                    cliente.save()
                else:
                    empleado = Empleado.objects.filter(correo__iexact=email).first()
                    if empleado:
                        empleado.reset_token = token
                        empleado.save()
                reset_url = request.build_absolute_uri(
                    reverse('login:password_reset_confirm', args=[token])
                )
                send_mail(
                    'Restablecer contraseña',
                    f'Para restablecer tu contraseña haz clic aquí: {reset_url}',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                success = "Te hemos enviado un correo para restablecer tu contraseña."
            else:
                error = "El correo no está registrado."
    else:
        form = PasswordResetForm()
    return render(request, 'login/password_reset.html', {'form': form, 'success': success, 'error': error})

def password_reset_confirm_view(request, token):
    error = None
    success = None
    cliente = Cliente.objects.filter(reset_token=token).first()
    empleado = Empleado.objects.filter(reset_token=token).first()
    user = None
    profile = None
    if cliente:
        user = cliente.user
        profile = cliente
    elif empleado:
        user = User.objects.filter(email__iexact=empleado.correo).first()
        profile = empleado
    if not user:
        error = "Token inválido o expirado."
    elif request.method == 'POST':
        form = SetNewPasswordForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            user.set_password(password)
            user.save()
            profile.reset_token = ''
            profile.save()
            success = "Contraseña restablecida correctamente. Ya puedes iniciar sesión."
    else:
        form = SetNewPasswordForm()
    return render(request, 'login/login.html', {
        'show_set_password_form': True,
        'form_set_password': form,
        'set_password_error': error,
        'set_password_success': success,
    })