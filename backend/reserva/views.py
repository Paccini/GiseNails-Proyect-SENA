from django.http import JsonResponse
from django.shortcuts import render
from empleados.models import Empleado
from servicio.models import Servicio
from reserva.models import HorarioDisponible, Reserva

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
            servicio_id = request.POST.get("servicio")
            hora_id = request.POST.get("hora")

            gestora = Empleado.objects.get(id=gestora_id)
            servicio = Servicio.objects.get(id=servicio_id)
            hora = HorarioDisponible.objects.get(id=hora_id)

            Reserva.objects.create(
                gestora=gestora,
                servicio=servicio,
                hora=hora
            )

            return JsonResponse({"success": True})

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
    ocupados = Reserva.objects.filter(gestora_id=gestora_id, hora__dia=fecha).values_list('hora_id', flat=True)
    disponibles = horarios.exclude(id__in=ocupados)
    data = [f"{h.hora.strftime('%H:%M')}" for h in disponibles]
    return JsonResponse({'horarios': data})
