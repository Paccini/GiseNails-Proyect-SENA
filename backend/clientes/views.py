from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.cache import never_cache
from django.contrib.auth import login as auth_login
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from .forms import RegistroClienteForm, ClienteForm
from clientes.models import Cliente
from clientes.forms import RegistroClienteForm
from reserva.models import Reserva
from reserva.forms import ReservaForm
from empleados.models import Empleado
from servicio.models import Servicio
from reserva.models import HorarioDisponible
from django.contrib import messages
from django.http import JsonResponse, Http404, HttpResponse  # <-- agregar si no está
from datetime import datetime
from cryptography.fernet import Fernet
from django.conf import settings
from cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken
from reserva.views import completar_reserva
from reserva.views import decrypt_id
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

fernet = Fernet(settings.ENCRYPT_KEY)
def encrypt_id(pk: int) -> str:
    """Convierte un ID normal en uno cifrado"""
    return fernet.encrypt(str(pk).encode()).decode()

def decrypt_id(token: str) -> int:
    """Convierte un token cifrado en el ID real"""
    return int(fernet.decrypt(token.encode()).decode())

@login_required
@never_cache
def panel_cliente(request):
    try:
        cliente = Cliente.objects.get(user=request.user)
    except Cliente.DoesNotExist:
        return redirect('clientes:registro')

    # filtros desde querystring
    estado = request.GET.get('estado', '')  # '' muestra todos
    fecha_inicio = request.GET.get('fecha_inicio', '').strip()
    fecha_fin = request.GET.get('fecha_fin', '').strip()
    page = request.GET.get('page', 1)

    reservas_qs = Reserva.objects.filter(cliente=cliente).order_by('-fecha', '-hora')

    # Filtrar por estado
    if estado:
        reservas_qs = reservas_qs.filter(estado=estado)

    # Filtrar por rango de fechas
    if fecha_inicio:
        try:
            fecha_inicio_obj = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            reservas_qs = reservas_qs.filter(fecha__gte=fecha_inicio_obj)
        except Exception:
            pass
    
    if fecha_fin:
        try:
            fecha_fin_obj = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            reservas_qs = reservas_qs.filter(fecha__lte=fecha_fin_obj)
        except Exception:
            pass

    paginator = Paginator(reservas_qs, 3)  # 4 por página
    reservas_page = paginator.get_page(page)

    # resto del contexto como antes, + variables de filtro/paginación
    eliminadas = request.GET.get('notifs_eliminadas', '')
    eliminadas_ids = [int(x) for x in eliminadas.split(',') if x.isdigit()]
    notificaciones = []
    for reserva in reservas_qs.order_by('-fecha_creacion')[:10]:
        if reserva.pk not in eliminadas_ids:
            notificaciones.append({
                'id': reserva.pk,
                'icon': 'bi-calendar-check' if reserva.estado == 'confirmada' else 'bi-calendar',
                'texto': f'Cita {reserva.get_estado_display()} para el {reserva.fecha.strftime("%d/%m/%Y")} a las {reserva.hora}',
                'fecha': reserva.fecha_creacion.strftime('%d/%m/%Y %H:%M')
            })

    form = RegistroClienteForm(instance=cliente)
    gestoras = Empleado.objects.all()
    servicios = Servicio.objects.all()
    horarios = HorarioDisponible.objects.all()
    # Manejo de alertas/modales desde la URL (por redirect después de editar perfil)
    show_cita_alert = request.session.pop('show_cita_alert', True)
    show_modal = False
    update_error = None
    update_success = None
    # Si la URL contiene ?success=1, mostramos modal con mensaje de éxito
    if request.GET.get('success') == '1':
        show_modal = True
        update_success = "¡Datos actualizados correctamente!"

    return render(request, 'clientes/panel.html', {
        'cliente': cliente,
        'reservas': reservas_page,
        'form': form,
        'user': request.user,
        'notificaciones': notificaciones,
        'gestoras': gestoras,
        'servicios': servicios,
        'horarios': horarios,
        'show_cita_alert': show_cita_alert,
        'filter_estado': estado,
        'filter_fecha_inicio': fecha_inicio,
        'filter_fecha_fin': fecha_fin,
        'show_modal': show_modal,
        'update_error': update_error,
        'update_success': update_success,
    })


@never_cache
@login_required(login_url='login:login')
def editar_perfil(request):
    try:
        cliente = Cliente.objects.get(user=request.user)
    except Cliente.DoesNotExist:
        return redirect('login:login')
    update_error = None
    update_success = None
    show_modal = False
    if request.method == 'POST':
        form = RegistroClienteForm(request.POST, instance=cliente)
        show_modal = True
        if form.is_valid():
            old_password = form.cleaned_data.get('old_password')
            new_password = form.cleaned_data.get('new_password')
            user = request.user
            if new_password:
                if not old_password or not user.check_password(old_password):
                    update_error = "La contraseña actual es incorrecta. No se realizaron cambios."
                    return render(request, 'clientes/panel.html', {
                        'cliente': cliente,
                        'reservas': Reserva.objects.filter(cliente=cliente),
                        'form': form,
                        'user': request.user,
                        'show_modal': True,
                        'update_error': update_error,
                        'update_success': None,
                        'notificaciones': [],
                    })
                else:
                    user.set_password(new_password)
                    user.save()
            form.save()
            return redirect('/clientes/panel/?success=1')
        else:
            update_error = "Corrige los errores del formulario."
            return render(request, 'clientes/panel.html', {
                'cliente': cliente,
                'reservas': Reserva.objects.filter(cliente=cliente),
                'form': form,
                'user': request.user,
                'show_modal': True,
                'update_error': update_error,
                'update_success': None,
                'notificaciones': [],
            })
    else:
        form = RegistroClienteForm(instance=cliente)
    # Mostrar alerta de éxito si viene en la URL
    update_success = None
    if request.GET.get('success') == '1':
        update_success = "¡Datos actualizados correctamente!"
        show_modal = True
    return render(request, 'clientes/panel.html', {
        'cliente': cliente,
        'reservas': Reserva.objects.filter(cliente=cliente),
        'form': form,
        'user': request.user,
        'show_modal': show_modal,
        'update_error': None,
        'update_success': update_success,
        'notificaciones': [],
    })
    

def logout_view(request):
    logout(request)
    return redirect('login:login')


@method_decorator(never_cache, name='dispatch')
class ClienteListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Cliente
    template_name = 'clientes/cliente_list.html'
    context_object_name = 'object_list'
    paginate_by = 5

    def test_func(self):
        return self.request.user.is_staff

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get('q', '')
        if q:
            queryset = queryset.filter(nombre__icontains=q)
        return queryset

@method_decorator(never_cache, name='dispatch')
class ClienteDetailView(DetailView):
    model = Cliente
    template_name = 'clientes/cliente_detail.html'
    context_object_name = 'cliente'

    def get_object(self, queryset=None):
        token = self.kwargs.get('token')
        if not token:
            raise Http404("Token no proporcionado")
        try:
            decrypted_id = fernet.decrypt(token.encode()).decode()
            return Cliente.objects.get(pk=decrypted_id)
        except (InvalidToken, Cliente.DoesNotExist):
            raise Http404("Token inválido o cliente no encontrado")

@method_decorator(never_cache, name='dispatch')
class ClienteCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Cliente
    form_class = RegistroClienteForm  # <-- Cambia ClienteForm por RegistroClienteForm
    template_name = 'clientes/cliente_form.html'
    success_url = reverse_lazy('clientes:cliente_list')

    def test_func(self):
        return self.request.user.is_staff

class ClienteUpdateView(UpdateView):
    model = Cliente
    form_class = RegistroClienteForm
    template_name = 'clientes/cliente_form.html'
    success_url = reverse_lazy('clientes:cliente_list')

    def get_object(self, queryset=None):
        token = self.kwargs.get('token')
        pk = decrypt_id(token)
        return get_object_or_404(Cliente, pk=pk)

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.object.user
        new_password = self.request.POST.get('new_password', '').strip()
        old_password = self.request.POST.get('old_password', '').strip()
        if new_password:
            if user.check_password(old_password):
                user.set_password(new_password)
                user.save()
                self.request.session['update_success'] = 'Contraseña actualizada correctamente.'
            else:
                self.request.session['update_error'] = 'La contraseña actual es incorrecta.'
        else:
            self.request.session['update_success'] = 'Datos actualizados correctamente.'
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['update_error'] = self.request.session.pop('update_error', None)
        context['update_success'] = self.request.session.pop('update_success', None)
        return context

@method_decorator(never_cache, name='dispatch')
class ClienteDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Cliente
    template_name = 'clientes/cliente_confirm_delete.html'
    success_url = reverse_lazy('clientes:cliente_list')

    def test_func(self):
        return self.request.user.is_staff

    def delete(self, request, *args, **kwargs):
        """
        No eliminar físicamente. Alternar campo 'activo'.
        No permitir deshabilitar si el cliente tiene reservas pendientes/confirmadas.
        """
        self.object = self.get_object()
        # Si se intenta deshabilitar (object.activo True) comprobamos reservas
        if self.object.activo:
            tiene_reservas = Reserva.objects.filter(cliente=self.object, estado__in=['pendiente', 'confirmada']).exists()
            if tiene_reservas:
                messages.error(request, "No se puede deshabilitar: el cliente tiene reservas pendientes o confirmadas.")
                return redirect(self.success_url)
        # Alterna activo
        self.object.activo = not self.object.activo
        self.object.save()
        estado = "habilitado" if self.object.activo else "deshabilitado"
        messages.success(request, f"Cliente {self.object.nombre} {estado}.")
        return redirect(self.success_url)

def registro_cliente(request):
    if request.method == 'POST':
        form = RegistroClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('clientes:login')
        else:
            # Si hay errores, renderiza el formulario con los datos y errores
            return render(request, 'clientes/registro.html', {'form': form})
    else:
        form = RegistroClienteForm()
    return render(request, 'clientes/registro.html', {'form': form})


@login_required
@never_cache
def agendar_reserva(request):
    cliente = get_object_or_404(Cliente, user=request.user)
    gestoras = Empleado.objects.all()
    servicios = Servicio.objects.all()
    horarios = HorarioDisponible.objects.all()
    if request.method == 'POST':
        fecha = request.POST.get('fecha')
        hora_id = request.POST.get('hora')
        gestora_id = request.POST.get('gestora')
        servicio_id = request.POST.get('servicio')
        observaciones = request.POST.get('observaciones', '')
        if fecha and hora_id and gestora_id and servicio_id:
            Reserva.objects.create(
                cliente=cliente,
                gestora_id=gestora_id,
                servicio_id=servicio_id,
                hora_id=hora_id,
                fecha=fecha,
                estado='pendiente'
            )
            return redirect('clientes:panel')
    return render(request, 'clientes/panel.html', {
        'cliente': cliente,
        'user': request.user,
        'gestoras': gestoras,
        'servicios': servicios,
        'horarios': horarios,
        'form': RegistroClienteForm(instance=cliente),
        'reservas': Reserva.objects.filter(cliente=cliente).exclude(estado='cancelada')
    })

@login_required
@never_cache
def cancelar_reserva(request, token):
    try:
        real_pk = decrypt_id(token)
    except:
        return redirect('clientes:panel')

    cliente = get_object_or_404(Cliente, user=request.user)
    reserva = get_object_or_404(Reserva, pk=real_pk, cliente=cliente)

    if request.method == 'POST':
        reserva.delete()
        return redirect('clientes:panel')

    return render(request, 'clientes/cancelar_reserva.html', {'reserva': reserva})

@login_required
@never_cache
def confirmar_reserva(request, pk):
    try:
        real_pk = decrypt_id(pk)
    except:
        return redirect('clientes:panel')

    cliente = get_object_or_404(Cliente, user=request.user)
    reserva = get_object_or_404(Reserva, pk=real_pk, cliente=cliente)

    
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        if nuevo_estado in dict(Reserva.ESTADO_CHOICES):
            reserva.estado = nuevo_estado
            reserva.save()
    return redirect('clientes:cliente_list')


def toggle_cliente_activo(request, pk):
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'No autorizado.'}, status=403)

    try:
        real_pk = decrypt_id(pk)
    except:
        return JsonResponse({'success': False, 'error': 'Token inválido.'}, status=400)

    cliente = get_object_or_404(Cliente, pk=real_pk)

    if cliente.activo:
        tiene_reservas = Reserva.objects.filter(cliente=cliente, estado__in=['pendiente', 'confirmada']).exists()
        if tiene_reservas:
            return JsonResponse({'success': False, 'error': 'El cliente tiene reservas pendientes o confirmadas.'})

    cliente.activo = not cliente.activo
    cliente.save()
    return JsonResponse({'success': True, 'activo': cliente.activo})

@login_required
@never_cache
def descargar_cita_pdf(request, token):
    try:
        real_pk = decrypt_id(token)
    except Exception:
        return redirect('clientes:panel')

    cliente = get_object_or_404(Cliente, user=request.user)
    reserva = get_object_or_404(Reserva, pk=real_pk, cliente=cliente)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=Cita_{reserva.pk}.pdf'

    p = canvas.Canvas(response, pagesize=letter)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, 750, "Comprobante de Cita - GiseNails")
    p.setFont("Helvetica", 12)
    p.drawString(50, 720, f"Cliente: {reserva.cliente.nombre}")
    p.drawString(50, 700, f"Servicio: {reserva.servicio}")
    p.drawString(50, 680, f"Gestora: {reserva.gestora}")
    p.drawString(50, 660, f"Fecha: {reserva.fecha.strftime('%d/%m/%Y')}")
    p.drawString(50, 640, f"Hora: {reserva.hora}")
    p.drawString(50, 620, f"Estado: {reserva.get_estado_display()}")
    p.drawString(50, 600, f"Precio: ${reserva.servicio.precio:,}")
    p.showPage()
    p.save()
    return response
