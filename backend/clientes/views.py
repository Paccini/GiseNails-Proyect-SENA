from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .forms import RegistroClienteForm, ClienteForm
from .models import Cliente
# from citas.models import Cita
# from citas.forms import CitaForm
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.core.paginator import Paginator

# @method_decorator(never_cache, name='dispatch')
# class ClienteListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
#     model = Cliente
#     template_name = 'clientes/cliente_list.html'
#     context_object_name = 'object_list'
#     paginate_by = 5

#     def test_func(self):
#         return self.request.user.is_staff

#     def get_queryset(self):
#         queryset = super().get_queryset()
#         q = self.request.GET.get('q', '')
#         if q:
#             queryset = queryset.filter(nombre__icontains=q)
#         return queryset

# @method_decorator(never_cache, name='dispatch')
# class ClienteDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
#     model = Cliente
#     template_name = 'clientes/cliente_detail.html'

#     def test_func(self):
#         return self.request.user.is_staff

# @method_decorator(never_cache, name='dispatch')
# class ClienteCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
#     model = Cliente
#     form_class = ClienteForm
#     template_name = 'clientes/cliente_form.html'
#     success_url = reverse_lazy('clientes:cliente_list')

#     def test_func(self):
#         return self.request.user.is_staff

# @method_decorator(never_cache, name='dispatch')
# class ClienteUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
#     model = Cliente
#     form_class = ClienteForm
#     template_name = 'clientes/cliente_form.html'
#     success_url = reverse_lazy('clientes:cliente_list')

#     def test_func(self):
#         return self.request.user.is_staff

# @method_decorator(never_cache, name='dispatch')
# class ClienteDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
#     model = Cliente
#     template_name = 'clientes/cliente_confirm_delete.html'
#     success_url = reverse_lazy('clientes:cliente_list')

#     def test_func(self):
#         return self.request.user.is_staff

def registro_cliente(request):
    if request.method == 'POST':
        form = RegistroClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('adminpanel:login')
    else:
        form = RegistroClienteForm()
    return render(request, 'adminpanel/login.html', {
        'form': form,
        'registro': True  # Indicador para mostrar el formulario de registro
    })

# @login_required
# @never_cache
# def panel_cliente(request):
#     try:
#         cliente = Cliente.objects.get(user=request.user)
#     except Cliente.DoesNotExist:
#         return redirect('clientes:registro')
#     citas = Cita.objects.filter(cliente=cliente)
#     return render(request, 'clientes/panel.html', {'citas': citas})

# @login_required
# @never_cache
# def agendar_cita(request):
#     cliente = get_object_or_404(Cliente, user=request.user)
#     if request.method == 'POST':
#         form = CitaForm(request.POST)
#         if form.is_valid():
#             cita = form.save(commit=False)
#             cita.cliente = cliente
#             cita.save()
#             return redirect('clientes:panel')
#     else:
#         form = CitaForm()
#     return render(request, 'clientes/agendar_cita.html', {'form': form})

# @login_required
# @never_cache
# def cancelar_cita(request, pk):
#     cliente = get_object_or_404(Cliente, user=request.user)
#     cita = get_object_or_404(Cita, pk=pk, cliente=cliente)
#     if request.method == 'POST':
#         cita.delete()
#         return redirect('clientes:panel')
#     return render(request, 'clientes/cancelar_cita.html', {'cita': cita})
