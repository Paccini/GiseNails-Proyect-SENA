from django.shortcuts import render, redirect
from .forms import RegistroClienteForm

def panel_cliente(request):
    # Vista para clientes
    return render(request, 'clientes/panel.html')

def registro_cliente(request):
    if request.method == 'POST':
        form = RegistroClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login:login')
    else:
        form = RegistroClienteForm()
    return render(request, 'clientes/registro.html', {'form': form})