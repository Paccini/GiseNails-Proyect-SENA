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


@never_cache
@login_required(login_url='login:login')
def panel_cliente(request):
    # Si el usuario no está autenticado, redirigir a la página de inicio de sesión
    if not request.user.is_authenticated:
        return redirect('login:login')
    try:
        cliente = Cliente.objects.get(user=request.user)
    except Cliente.DoesNotExist:
        return redirect('login:login')
    # Renderiza el panel con contenido
    return render(request, 'clientes/panel.html', {'cliente': cliente, 'user': request.user})


def registro_cliente(request):
    # detecta reserva pendiente en sesión para prellenar email y mostrar mensaje
    pending = request.session.get('pending_reserva')
    initial = {}
    if pending:
        initial = {
            'nombre': pending.get('nombre', ''),
            'correo': pending.get('correo', ''),
            'telefono': pending.get('telefono', ''),
        }

    if request.method == 'POST':
        form = RegistroClienteForm(request.POST)
        # DEBUG rápido: descomenta para ver POST en consola
        # print('POST registro:', request.POST)
        if form.is_valid():
            cliente = form.save()  # que devuelva la instancia Cliente
            # si usas UserCreationForm asegúrate de enlazar user<>cliente según tu modelo
            try:
                user = cliente.user  # si tu modelo Cliente crea/relaciona user
            except Exception:
                user = None
            if user:
                auth_login(request, user)
            # si hay reserva pendiente, redirigir para completarla
            if request.session.get('pending_reserva'):
                return redirect('/reserva/completar-reserva/')
            # si no hay pending, mostrar modal de éxito en reserva o llevar a inicio
            return redirect('/reserva/?success=1')
        else:
            # render con errores (se verán en la plantilla si la incluíste)
            return render(request, 'clientes/registro.html', {'form': form, 'prefill_email': initial.get('correo'), 'pending_message': bool(pending)})
    else:
        form = RegistroClienteForm(initial=initial)
        if initial.get('correo'):
            try:
                form.fields['correo'].widget.attrs['readonly'] = True
            except Exception:
                pass
        return render(request, 'clientes/registro.html', {'form': form, 'prefill_email': initial.get('correo'), 'pending_message': bool(pending)})

@never_cache
@login_required(login_url='login:login')
def editar_perfil(request):
    try:
        cliente = Cliente.objects.get(user=request.user)
    except Cliente.DoesNotExist:
        return redirect('login:login')
    if request.method == 'POST':
        form = RegistroClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            
            return redirect('clientes:panel')
    else:
        form = RegistroClienteForm(instance=cliente)
    return render(request, 'clientes/panel.html', {
        'cliente': cliente, 
        'user': request.user, 
        'form': form})
    

@never_cache
@login_required(login_url='login:login')
def panel_cliente(request):
    if not request.user.is_authenticated:
        return redirect('login:login')
    try:
        cliente = Cliente.objects.get(user=request.user)
    except Cliente.DoesNotExist:
        return redirect('login:login')
    form = RegistroClienteForm(instance=cliente)  # <-- Agrega esto
    return render(request, 'clientes/panel.html', {'cliente': cliente, 'user': request.user, 'form': form})

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
def panel_cliente(request):
    try:
        cliente = Cliente.objects.get(user=request.user)
    except Cliente.DoesNotExist:
        return redirect('clientes:registro')
    reservas = Reserva.objects.filter(cliente=cliente)
    return render(request, 'clientes/panel.html', {'reservas': reservas})

@login_required
@never_cache
def agendar_reserva(request):
    cliente = get_object_or_404(Cliente, user=request.user)
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.cliente = cliente
            reserva.save()
            return redirect('clientes:panel')
    else:
        form = ReservaForm()
    return render(request, 'clientes/agendar_reserva.html', {'form': form})

@login_required
@never_cache
def cancelar_reserva(request, pk):
    cliente = get_object_or_404(Cliente, user=request.user)
    reserva = get_object_or_404(Reserva, pk=pk, cliente=cliente)
    if request.method == 'POST':
        reserva.delete()
        return redirect('clientes:panel')
    return render(request, 'clientes/cancelar_reserva.html', {'reserva': reserva})