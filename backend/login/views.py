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
from django.db.models import Count
from django.http import HttpResponse
from .forms import UpdateUserForm
from empleados.models import Empleado


def login_view(request):
    error = None
    prefill_email = None
    password_only = False
    if request.method == 'POST':
        email = request.POST.get('username')
        password = request.POST.get('password')
        # Buscar usuario por email
        user_qs = User.objects.filter(email__iexact=email)
        user = user_qs.first()
        username = email if user is None else user.username

        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Antes de iniciar sesión, comprobar si está relacionado con Cliente o Empleado inactivo
            # 1) Cliente asociado al user
            cliente_obj = Cliente.objects.filter(user=user).first()
            if cliente_obj is not None and not cliente_obj.activo:
                # Cuenta de cliente deshabilitada
                error = "Tu cuenta está inactiva, contáctate con el administrador."
                # Asegurarse de no dejar sesión iniciada
                try:
                    logout(request)
                except Exception:
                    pass
                return render(request, 'login/login.html', {'form': {}, 'error': error, 'prefill_email': None, 'password_only': False})

            # 2) Empleado asociado por correo
            empleado_obj = Empleado.objects.filter(correo__iexact=user.email).first()
            if empleado_obj is not None and not empleado_obj.activo:
                # Cuenta de empleado deshabilitada
                error = "Tu cuenta está inactiva, contáctate con el administrador."
                try:
                    logout(request)
                except Exception:
                    pass
                return render(request, 'login/login.html', {'form': {}, 'error': error, 'prefill_email': None, 'password_only': False})

            # Si pasa validaciones, iniciar sesión
            login(request, user)
            # Cliente -> panel clientes
            if cliente_obj:
                # Si hay reserva pendiente, completar la reserva
                if request.session.get('pending_reserva'):
                    return redirect('/reserva/completar-reserva/')
                request.session['show_cita_alert'] = True
                return redirect('clientes:panel')
            # Empleado -> panel de empleados (buscar por correo en lugar de user)
            if Empleado.objects.filter(correo__iexact=user.email).exists():
                 return redirect('empleados:panel_empleado')
            # Staff / superuser -> dashboard admin
            if user.is_staff or user.is_superuser:
                return redirect('login:dashboard')
            # Si no encaja en ningún tipo permitido
            error = "No tienes permisos para acceder."
        else:
            error = "Usuario o contraseña incorrectos."

    # Si hay una reserva pendiente, prellenar el correo y mostrar modo "solo contraseña"
    if request.session.get('pending_reserva'):
        pending = request.session.get('pending_reserva')
        prefill_email = pending.get('correo')
        password_only = True

    return render(request, 'login/login.html', {'form': {}, 'error': error, 'prefill_email': prefill_email, 'password_only': password_only})


@never_cache
@login_required(login_url='login:login')
def admin_panel(request):
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect('login:login')
    return redirect('login:dashboard')

def logout_view(request):
    logout(request)
    return redirect('login:login')

@login_required
@user_passes_test(lambda u: u.is_staff)
@never_cache
def dashboard(request):
    clientes_count = Cliente.objects.count()
    productos_count = Producto.objects.count()
    servicios_count = Servicio.objects.count()
    ventas_total = sum([cita.servicio.precio for cita in Reserva.objects.filter(estado='realizada') if hasattr(cita, 'servicio') and cita.servicio])

    citas_realizadas = (
        Reserva.objects
        .filter(fecha__year=timezone.now().year, estado='realizada')
        .values_list('fecha__month')
        .annotate(total=Count('id'))
        .order_by('fecha__month')
    )
    meses = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
    datos_citas = [0]*12
    for mes, total in citas_realizadas:
        datos_citas[mes-1] = total

    # Notificaciones: solo citas creadas y clientes registrados
    notificaciones = []
    # Últimas 5 citas creadas
    for cita in Reserva.objects.order_by('-fecha')[:5]:
        notificaciones.append({
            'icon': 'bi-calendar-check',
            'texto': f'Cita creada para {cita.cliente}',
            'fecha': cita.fecha.strftime('%d/%m/%Y %H:%M')
        })
    # Últimos 5 clientes registrados
    for cliente in Cliente.objects.order_by('-id')[:5]:
        notificaciones.append({
            'icon': 'bi-person-plus',
            'texto': f'Cliente registrado: {cliente}',
            'fecha': cliente.fecha_registro.strftime('%d/%m/%Y %H:%M') if hasattr(cliente, 'fecha_registro') else ''
        })

    context = {
        'clientes_count': clientes_count,
        'productos_count': productos_count,
        'servicios_count': servicios_count,
        'ventas_total': ventas_total,
        'datos_citas': datos_citas,
        'meses': meses,
        'notificaciones': notificaciones,
    }
    return render(request, 'dashboard.html', context)

@login_required(login_url='login:login')
def update_user(request):
    update_error = None
    update_success = None
    show_modal = False
    if request.method == 'POST':
        form = UpdateUserForm(request.POST)
        show_modal = True  # Siempre mostrar el modal tras POST
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