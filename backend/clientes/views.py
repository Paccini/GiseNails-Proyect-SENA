from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache

from .forms import RegistroClienteForm
from .models import Cliente


@never_cache
@login_required(login_url='login:login')
def panel_cliente(request):
    # Si el usuario no está autenticado, redirigir a la página de inicio de sesión
    if not request.user.is_authenticated:
        return redirect('login:login')
    try:
        cliente = Cliente.objects.get(user=request.user)
    except Cliente.DoesNotExist:
        return redirect('login:login')
    # Renderiza el panel con contenido
    return render(request, 'clientes/panel.html', {'cliente': cliente, 'user': request.user})


def registro_cliente(request):
    if request.method == 'POST':
        form = RegistroClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login:login')
    else:
        form = RegistroClienteForm()
    return render(request, 'clientes/registro.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login:login')