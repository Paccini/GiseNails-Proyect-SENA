from django.contrib.auth import logout
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator

from .forms import RegistroClienteForm
from .models import Cliente


@never_cache
def panel_cliente(request):
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