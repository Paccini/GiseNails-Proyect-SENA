from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from clientes.models import Cliente

def login_view(request):
    error = None
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
            if user.is_superuser or user.is_staff:
                return redirect('login:admin_panel')  # Redirige a la vista admin
            elif Cliente.objects.filter(user=user).exists():
                return redirect('clientes:panel')
            else:
                error = "No tienes permisos para acceder."
        else:
            error = "Usuario o contraseña incorrectos."
    return render(request, 'login/login.html', {'form': {}, 'error': error})

def admin_panel(request):
    if not request.user.is_authenticated or not (request.user.is_superuser or request.user.is_staff):
        return redirect('login:login')
    return render(request, 'base_admin.html')

def logout_view(request):
    logout(request)
    return redirect('login:login')