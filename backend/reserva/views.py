from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from empleados.models import Empleado
from servicio.models import Servicio
from reserva.models import HorarioDisponible, Reserva
from .forms import ReservaForm
from clientes.models import Cliente
from productos.models import Producto
from servicio.models import Servicio as ServicioModel
from django.db.models import Count
from django.utils import timezone
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.decorators.cache import never_cache
from django.core.paginator import Paginator

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

# --- Vistas administrativas de Reservas ---

@login_required
@user_passes_test(lambda u: u.is_staff)
@never_cache
def home(request):
    fecha = request.GET.get('fecha', '')
    usuario = request.GET.get('usuario', '')
    reservas = Reserva.objects.all()
    if fecha:
        reservas = reservas.filter(fecha=fecha)
    if usuario:
        reservas = reservas.filter(cliente__nombre__icontains=usuario)
    paginator = Paginator(reservas, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'reservas': page_obj,
        'fecha': fecha,
        'usuario': usuario,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
        'paginator': paginator,
    }
    return render(request, 'reservas/home.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
@never_cache
def agregar_reserva(request):
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('reserva:home')
    else:
        form = ReservaForm()
    context = {'form': form}
    return render(request, 'reservas/agregar.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
@never_cache
def editar_reserva(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    from .forms import ReservaEditForm
    if request.method == 'POST':
        form = ReservaEditForm(request.POST, instance=reserva)
        if form.is_valid():
            form.save()
            return redirect('reserva:home')
    else:
        form = ReservaEditForm(instance=reserva)
    context = {'form': form}
    return render(request, 'reservas/editar.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
@never_cache
def eliminar_reserva(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    if request.method == 'POST':
        reserva.delete()
        return redirect("reserva:home")
    return render(request, 'reservas/eliminar.html', {'reserva': reserva})

@login_required
@user_passes_test(lambda u: u.is_staff)
@never_cache
def dashboard(request):
    clientes_count = Cliente.objects.count()
    productos_count = Producto.objects.count()
    servicios_count = ServicioModel.objects.count()
    ventas_total = sum([reserva.servicio.precio for reserva in Reserva.objects.filter(estado='realizada') if hasattr(reserva, 'servicio') and reserva.servicio])

    reservas_realizadas = (
        Reserva.objects
        .filter(fecha__year=timezone.now().year, estado='realizada')
        .values_list('fecha__month')
        .annotate(total=Count('id'))
        .order_by('fecha__month')
    )
    meses = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
    datos_reservas = [0]*12
    for mes, total in reservas_realizadas:
        datos_reservas[mes-1] = total

    context = {
        'clientes_count': clientes_count,
        'productos_count': productos_count,
        'servicios_count': servicios_count,
        'ventas_total': ventas_total,
        'datos_reservas': datos_reservas,
        'meses': meses,
    }
    return render(request, 'dashboard.html', context)

class ReservaCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Reserva
    form_class = ReservaForm
    template_name = 'reservas/agregar.html'
    success_url = reverse_lazy('reserva:home')

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        # El formulario ya tiene el cliente seleccionado
        self.object = form.save()
        return super().form_valid(form)
