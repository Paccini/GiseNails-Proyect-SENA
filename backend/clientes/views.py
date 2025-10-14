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
from reserva.models import Reserva
from reserva.forms import ReservaForm
from empleados.models import Empleado
from servicio.models import Servicio
from reserva.models import HorarioDisponible


@login_required
@never_cache
def panel_cliente(request):
    try:
        cliente = Cliente.objects.get(user=request.user)
    except Cliente.DoesNotExist:
        return redirect('clientes:registro')
    reservas = Reserva.objects.filter(cliente=cliente).exclude(estado='cancelada')
    eliminadas = request.GET.get('notifs_eliminadas', '')
    eliminadas_ids = [int(x) for x in eliminadas.split(',') if x.isdigit()]
    notificaciones = []
    for reserva in reservas.order_by('-fecha_creacion')[:10]:
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
    show_cita_alert = request.session.pop('show_cita_alert', True)
    return render(request, 'clientes/panel.html', {
        'cliente': cliente,
        'reservas': reservas,
        'form': form,
        'user': request.user,
        'notificaciones': notificaciones,
        'gestoras': gestoras,
        'servicios': servicios,
        'horarios': horarios,
        'show_cita_alert': show_cita_alert,
    })

def registro_cliente(request):
    pending = request.session.get('pending_reserva')
    initial = {}
    # Solo autocompleta si hay pending y el correo NO está registrado
    if pending:
        from clientes.models import Cliente
        correo = pending.get('correo', '')
        if not Cliente.objects.filter(correo__iexact=correo).exists():
            initial = {
                'nombre': pending.get('nombre', ''),
                'correo': correo,
                'telefono': pending.get('telefono', ''),
            }

    if request.method == 'POST':
        form = RegistroClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save()
            try:
                user = cliente.user
            except Exception:
                user = None
            if user:
                from django.contrib.auth import login as auth_login
                auth_login(request, user)
            if request.session.get('pending_reserva'):
                return redirect('/reserva/completar-reserva/')
            return redirect('/reserva/?success=1')
        else:
            return render(request, 'clientes/registro.html', {
                'form': form,
                'prefill_email': initial.get('correo'),
                'pending_message': bool(pending)
            })
    else:
        form = RegistroClienteForm(initial=initial)
        if initial.get('correo'):
            try:
                form.fields['correo'].widget.attrs['readonly'] = True
            except Exception:
                pass
        return render(request, 'clientes/registro.html', {
            'form': form,
            'prefill_email': initial.get('correo'),
            'pending_message': bool(pending)
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
                    # Mostrar error y mantener modal abierto
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
                    from django.contrib.auth import update_session_auth_hash
                    update_session_auth_hash(request, user)
                    form.save()
                    return redirect('/clientes/panel/?success=1')
            else:
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
class ClienteDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Cliente
    template_name = 'clientes/cliente_detail.html'

    def test_func(self):
        return self.request.user.is_staff

@method_decorator(never_cache, name='dispatch')
class ClienteCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'clientes/cliente_form.html'
    success_url = reverse_lazy('clientes:cliente_list')

    def test_func(self):
        return self.request.user.is_staff

@method_decorator(never_cache, name='dispatch')
class ClienteUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'clientes/cliente_form.html'
    success_url = reverse_lazy('clientes:cliente_list')

    def test_func(self):
        return self.request.user.is_staff

@method_decorator(never_cache, name='dispatch')
class ClienteDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Cliente
    template_name = 'clientes/cliente_confirm_delete.html'
    success_url = reverse_lazy('clientes:cliente_list')

    def test_func(self):
        return self.request.user.is_staff

def registro_cliente(request):
    if request.method == 'POST':
        form = RegistroClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login:login')  # Si quieres redirigir después de registrar
    else:
        form = RegistroClienteForm()
    return render(request, 'clientes/registro.html', {
        'form': form,
        'registro': True
    })


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
def cancelar_reserva(request, pk):
    cliente = get_object_or_404(Cliente, user=request.user)
    reserva = get_object_or_404(Reserva, pk=pk, cliente=cliente)
    if request.method == 'POST':
        reserva.delete()
        return redirect('clientes:panel')
    return render(request, 'clientes/cancelar_reserva.html', {'reserva': reserva})

@login_required
@never_cache
def confirmar_reserva(request, pk):
    cliente = get_object_or_404(Cliente, user=request.user)
    reserva = get_object_or_404(Reserva, pk=pk, cliente=cliente)
    if request.method == 'POST' and reserva.estado == 'pendiente':
        reserva.estado = 'confirmada'
        reserva.save()
    return redirect('clientes:panel')