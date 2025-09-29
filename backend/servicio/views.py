from django.shortcuts import render
from .models import Servicio
from django.core.paginator import Paginator
from django.views.decorators.http import require_GET


@require_GET
def lista_servicios(request):
    servicios_list = Servicio.objects.all()
    paginator = Paginator(servicios_list, 3)  # 3 servicios por página
    page_number = request.GET.get('page')
    servicios = paginator.get_page(page_number)
    return render(request, 'servicios/lista_servicios.html', {'servicios': servicios})

# Create your views here.
