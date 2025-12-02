import urllib.parse # <-- ¡IMPORTACIÓN CLAVE!
from django.shortcuts import render, redirect, get_object_or_404, Http404
from django.core.paginator import Paginator
from django.views.decorators.http import require_GET
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required, user_passes_test

from .models import Servicio
from .forms import ServicioForm

# Importar tus funciones de cifrado/descifrado
from django.utils.http import urlsafe_base64_decode
from cryptography.fernet import Fernet
from django.conf import settings

# -----------------------------
# 🔐 Funciones de Cifrado/Descifrado
# -----------------------------

fernet = Fernet(settings.ENCRYPT_KEY)

def encrypt_id(pk):
    return fernet.encrypt(str(pk).encode()).decode()

def decrypt_id(token):
    # Nota: Fernet.decrypt() espera bytes de Base64 seguro para URL (sin %3D)
    return int(fernet.decrypt(token.encode()).decode())

# =============================
# LISTA CLIENTE (PÚBLICA)
# =============================
@require_GET
def lista_servicios(request):
    servicios_list = Servicio.objects.all()
    paginator = Paginator(servicios_list, 3)
    page_number = request.GET.get('page')
    servicios = paginator.get_page(page_number)

    mas_solicitados = Servicio.objects.all().order_by('-id')[:6]

    return render(request, 'servicios/lista_servicios.html', {
        'servicios': servicios,
        'mas_solicitados': mas_solicitados,
    })


# =============================
# LISTA ADMIN
# =============================
@login_required
@user_passes_test(lambda u: u.is_staff)
@never_cache
def servicio_list(request):
    q = request.GET.get('q', '')
    servicios = Servicio.objects.all()

    if q:
        servicios = servicios.filter(nombre__icontains=q)

    paginator = Paginator(servicios, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'servicios/servicio_list.html', {
        'servicios': page_obj,
        'q': q,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
        'paginator': paginator,
    })


# =============================
# CREAR SERVICIO
# =============================
@login_required
@user_passes_test(lambda u: u.is_staff)
@never_cache
def servicio_create(request):
    if request.method == 'POST':
        form = ServicioForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('servicio:servicio_list')
    else:
        form = ServicioForm()

    return render(request, 'servicios/servicio_form.html', {
        'form': form
    })


# =============================
# EDITAR SERVICIO (Corregido para usar token)
# =============================
@login_required
@user_passes_test(lambda u: u.is_staff)
@never_cache
def servicio_update(request, token): # <-- 'pk' cambiado a 'token'
    try:
        # 1. Decodificar URL para limpiar %3D, %2B, etc.
        clean_token = urllib.parse.unquote(token) 
        
        # 2. Desencriptar a ID real
        real_id = decrypt_id(clean_token) 
        servicio = get_object_or_404(Servicio, pk=real_id)
        
    except Exception:
        # Captura errores de Fernet (InvalidToken)
        raise Http404("ID de servicio inválido o no encontrado")

    if request.method == 'POST':
        form = ServicioForm(request.POST, request.FILES, instance=servicio)
        if form.is_valid():
            form.save()
            return redirect('servicio:servicio_list')
    else:
        form = ServicioForm(instance=servicio)

    return render(request, 'servicios/servicio_form.html', {
        'form': form,
        'servicio': servicio
    })


# =============================
# ELIMINAR SERVICIO (Corregido para usar token)
# =============================
@login_required
@user_passes_test(lambda u: u.is_staff)
@never_cache
def servicio_delete(request, token): # <-- 'pk' cambiado a 'token'
    try:
        # 1. Decodificar URL para limpiar %3D, %2B, etc.
        clean_token = urllib.parse.unquote(token) 
        
        # 2. Desencriptar a ID real
        real_id = decrypt_id(clean_token)
        servicio = get_object_or_404(Servicio, pk=real_id)
        
    except Exception:
        # Captura errores de Fernet (InvalidToken)
        raise Http404("ID de servicio inválido o no encontrado")

    if request.method == 'POST':
        servicio.delete()
        return redirect('servicio:servicio_list')

    return render(request, 'servicios/servicio_confirm_delete.html', {
        'servicio': servicio
    })


# =============================
# DETALLE (ADMIN - Corregido para usar token)
# =============================
@login_required
@user_passes_test(lambda u: u.is_staff)
@never_cache
def servicio_detail(request, token): # <-- 'pk' cambiado a 'token'
    try:
        # 1. Decodificar URL para limpiar %3D, %2B, etc.
        clean_token = urllib.parse.unquote(token) 
        
        # 2. Desencriptar a ID real
        real_id = decrypt_id(clean_token)
        servicio = get_object_or_404(Servicio, pk=real_id)
        
    except Exception:
        # Captura errores de Fernet (InvalidToken)
        raise Http404("ID de servicio inválido o no encontrado")
        
    return render(request, 'servicios/servicio_detail.html', {
        'servicio': servicio
    })