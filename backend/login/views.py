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


def login_view(request):
    error = None
    prefill_email = None
    password_only = False
    if request.method == 'POST':
        email = request.POST.get('username')
        password = request.POST.get('password')
        # Buscar usuario por email
        try:
            user = User.objects.get(email=email)
            username = user.username
        except User.DoesNotExist:
            username = email  # Por si el username es el email

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # si hay reserva pendiente en sesión, redirigir a completarla
            if request.session.get('pending_reserva'):
                return redirect('/reserva/completar-reserva/')
            if user.is_superuser or user.is_staff:
                return redirect('login:admin_panel')  # Redirige a la vista admin
            elif Cliente.objects.filter(user=user).exists():
                return redirect('clientes:panel')
            else:
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

    context = {
        'clientes_count': clientes_count,
        'productos_count': productos_count,
        'servicios_count': servicios_count,
        'ventas_total': ventas_total,
        'datos_citas': datos_citas,
        'meses': meses,
    }
    return render(request, 'dashboard.html', context)