from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from clientes.models import Cliente
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from productos.models import Producto
from servicio.models import Servicio

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
    return render(request, 'base_admin.html')

def logout_view(request):
    logout(request)
    return redirect('login:login')

@never_cache
@login_required(login_url='login:login')
def dashboard(request):
    # Ejemplo de datos para el dashboard
    clientes_count = Cliente.objects.count()
    productos_count = Producto.objects.count()
    servicios_count = Servicio.objects.count()
    ventas_total = 0  # Si tienes modelo de ventas, cámbialo
    meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun"]
    datos_citas = [5, 8, 12, 7, 10, 6]  # Simulado, reemplaza por tus datos

    context = {
        "clientes_count": clientes_count,
        "productos_count": productos_count,
        "servicios_count": servicios_count,
        "ventas_total": ventas_total,
        "meses": meses,
        "datos_citas": datos_citas,
    }
    return render(request, "dashboard.html", context)