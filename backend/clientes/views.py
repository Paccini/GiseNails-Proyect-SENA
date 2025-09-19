from django.shortcuts import render, redirect
from .forms import RegistroClienteForm

def panel_cliente(request):
    # Vista para clientes
    return render(request, 'clientes/panel.html')