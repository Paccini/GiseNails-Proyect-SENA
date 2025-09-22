
from django.shortcuts import render
from .models import Servicio
from django.views.decorators.http import require_GET

@require_GET
def lista_servicios(request):
	servicios = Servicio.objects.all()
	return render(request, 'servicios/lista_servicios.html', {'servicios': servicios})

@require_GET
def detalle_servicio(request, pk):
	from django.shortcuts import get_object_or_404
	servicio = get_object_or_404(Servicio, pk=pk)
	return render(request, 'servicios/detalle_servicio.html', {'servicio': servicio})

@require_GET
def inicio(request):
	return render(request, 'servicios/inicio.html')

# Create your views here.
