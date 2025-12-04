from django.urls import path
from . import views
from reserva import views as reserva_views
from .views import descargar_cita_pdf

app_name = 'clientes'

urlpatterns = [
    path('panel/', views.panel_cliente, name='panel'),
    path('agendar/', views.agendar_reserva, name='agendar'),

    # URLs que usan token encriptado
    path('cancelar/<str:token>/', views.cancelar_reserva, name='cancelar'),
    path('confirmar/<str:token>/', views.confirmar_reserva, name='confirmar'),

    # CRUD
    path('crear/', views.ClienteCreateView.as_view(), name='cliente_create'),
    path('', views.ClienteListView.as_view(), name='cliente_list'),
    path('<str:token>/', views.ClienteDetailView.as_view(), name='cliente_detail'),

    path('<str:token>/editar/', views.ClienteUpdateView.as_view(), name='cliente_update'),
    path('<str:token>/eliminar/', views.ClienteDeleteView.as_view(), name='cliente_delete'),

    # Otros
    path('editar-perfil/', views.editar_perfil, name='editar_perfil'),
    path('<str:token>/toggle-activo/', views.toggle_cliente_activo, name='cliente_toggle_activo'),

    path('abonar/<str:token>/', reserva_views.abonar_reserva, name='abonar_reserva'),
    path('pago-efectivo/<str:token>/', reserva_views.pago_efectivo, name='pago_efectivo'),

    path('pagar-completo/<str:token>/', reserva_views.pagar_completo, name='pagar_completo'),

    path('pagar-saldo/<str:token>/', reserva_views.pagar_saldo, name='pagar_saldo'),

    path('cita/<str:token>/pdf/', descargar_cita_pdf, name='descargar_cita_pdf'),
]