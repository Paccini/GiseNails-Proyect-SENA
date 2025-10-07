from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache
from django.contrib.auth import login as auth_login

from .forms import RegistroClienteForm
from clientes.models import Cliente


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
    # detecta reserva pendiente en sesión para prellenar email y mostrar mensaje
    pending = request.session.get('pending_reserva')
    initial = {}
    if pending:
        initial = {
            'nombre': pending.get('nombre', ''),
            'correo': pending.get('correo', ''),
            'telefono': pending.get('telefono', ''),
        }

    if request.method == 'POST':
        form = RegistroClienteForm(request.POST)
        # DEBUG rápido: descomenta para ver POST en consola
        # print('POST registro:', request.POST)
        if form.is_valid():
            cliente = form.save()  # que devuelva la instancia Cliente
            # si usas UserCreationForm asegúrate de enlazar user<>cliente según tu modelo
            try:
                user = cliente.user  # si tu modelo Cliente crea/relaciona user
            except Exception:
                user = None
            if user:
                auth_login(request, user)
            # si hay reserva pendiente, redirigir para completarla
            if request.session.get('pending_reserva'):
                return redirect('/reserva/completar-reserva/')
            # si no hay pending, mostrar modal de éxito en reserva o llevar a inicio
            return redirect('/reserva/?success=1')
        else:
            # render con errores (se verán en la plantilla si la incluíste)
            return render(request, 'clientes/registro.html', {'form': form, 'prefill_email': initial.get('correo'), 'pending_message': bool(pending)})
    else:
        form = RegistroClienteForm(initial=initial)
        if initial.get('correo'):
            try:
                form.fields['correo'].widget.attrs['readonly'] = True
            except Exception:
                pass
        return render(request, 'clientes/registro.html', {'form': form, 'prefill_email': initial.get('correo'), 'pending_message': bool(pending)})


def logout_view(request):
    logout(request)
    return redirect('login:login')