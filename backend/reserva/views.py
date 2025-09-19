from django.shortcuts import render
from django.http import JsonResponse
# from .models import HorarioDisponible

# from reserva import views
# Create your views here.
def reserva(request):
    return render(request, 'reserva/reserva.html')

def reserva2(request):
    return render(request, 'reserva/reserva2.html')

# def horarios_disponibles(request):
#     fecha = request.GET.get('fecha')
#     if not fecha:
#         return JsonResponse({'error': 'Fecha no proporcionada'}, status=400)
#     # Horarios fijos
#     horarios_fijos = HorarioDisponible.objects.all().order_by('hora')
#     # Horas ocupadas en la fecha
#     ocupadas = Cita.objects.filter(fecha=fecha).values_list('hora', flat=True)
#     # Horas libres
#     libres = [h.hora.strftime('%H:%M') for h in horarios_fijos if h.hora not in ocupadas]
#     return JsonResponse({'horarios': libres})