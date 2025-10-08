from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from empleados.models import Empleado
from servicio.models import Servicio
from reserva.models import HorarioDisponible, Reserva
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from clientes.models import Cliente
from django.db import transaction, IntegrityError

def reserva(request):
    gestoras = Empleado.objects.all()
    horarios = HorarioDisponible.objects.all()
    servicios = Servicio.objects.all()
    # Agrupa servicios por categoría
    servicios_por_categoria = {
        'manicure': servicios.filter(categoria='manicure'),
        'pedicure': servicios.filter(categoria='pedicure'),
        'estructura': servicios.filter(categoria='estructura'),
    }

    if request.method == "POST":
        try:
            gestora_id = request.POST.get("gestora")
            nombre_cliente = request.POST.get("nombre")
            telefono_cliente = request.POST.get("telefono")
            servicio_id = request.POST.get("servicio")
            hora_id = request.POST.get("hora")
            fecha_str = request.POST.get("fecha")
            correo_cliente = request.POST.get("correo")

            # Validaciones básicas: asegurar que los ids existen
            if not gestora_id or not servicio_id or not hora_id:
                return JsonResponse({"success": False, "error": "Selecciona gestora, servicio y horario."})

            try:
                gestora = Empleado.objects.get(id=gestora_id)
            except Empleado.DoesNotExist:
                return JsonResponse({"success": False, "error": "Gestora no encontrada."})

            try:
                servicio = Servicio.objects.get(id=servicio_id)
            except Servicio.DoesNotExist:
                return JsonResponse({"success": False, "error": "Servicio no encontrado."})

            try:
                hora = HorarioDisponible.objects.get(id=hora_id)
            except HorarioDisponible.DoesNotExist:
                return JsonResponse({"success": False, "error": "Horario no disponible (selecciona otro)."})

            # parsear fecha (se espera formato d/m/Y desde flatpickr)
            from datetime import datetime
            try:
                fecha = datetime.strptime(fecha_str, '%d/%m/%Y').date()
            except Exception:
                # intentar ISO (Y-m-d)
                fecha = datetime.fromisoformat(fecha_str).date()

            # Preparar datos de reserva para guardarlos en sesión y completar tras login/registro
            pending = {
                'gestora_id': gestora.id,
                'servicio_id': servicio.id,
                'hora_id': hora.id,
                'fecha': fecha.strftime('%Y-%m-%d'),
                'nombre': nombre_cliente,
                'telefono': telefono_cliente,
                'correo': correo_cliente,
            }

            # comprobar si el correo ya existe en clientes
            from clientes.models import Cliente
            cliente_obj = Cliente.objects.filter(correo__iexact=correo_cliente).first()
            request.session['pending_reserva'] = pending

            if cliente_obj:
                # ya existe: pedir login (solo contraseña)
                from django.urls import reverse
                login_url = reverse('login:login')
                return JsonResponse({"next": f"{login_url}?next=/completar-reserva/", "need": "login"})
            else:
                # no existe: redirigir a registro
                from django.urls import reverse
                registro_url = reverse('clientes:registro')
                return JsonResponse({"next": f"{registro_url}?next=/completar-reserva/", "need": "register"})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return render(request, 'reserva/reserva.html', {
        'gestoras': gestoras,
        'horarios': horarios,
        'servicios_por_categoria': servicios_por_categoria,
    })

def horarios_disponibles(request):
    gestora_id = request.GET.get('gestora_id')
    fecha = request.GET.get('fecha')
    horarios = HorarioDisponible.objects.all()
    # parsear fecha entrante (d/m/Y)
    from datetime import datetime
    try:
        fecha_obj = datetime.strptime(fecha, '%d/%m/%Y').date()
    except Exception:
        try:
            fecha_obj = datetime.fromisoformat(fecha).date()
        except Exception:
            return JsonResponse({'horarios': []})

    ocupados = Reserva.objects.filter(gestora_id=gestora_id, fecha=fecha_obj).values_list('hora_id', flat=True)
    disponibles = horarios.exclude(id__in=ocupados)
    # devolver id y texto para cada horario
    data = [{'id': h.id, 'hora': h.hora.strftime('%H:%M')} for h in disponibles]
    return JsonResponse({'horarios': data})
