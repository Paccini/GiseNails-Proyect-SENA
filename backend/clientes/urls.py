from django.urls import path
from . import views

app_name = 'clientes'

urlpatterns = [
    path('panel/', views.panel_cliente, name='panel'),
    path('agendar/', views.agendar_reserva, name='agendar'),

    # URLs que usan token encriptado
    path('cancelar/<str:token>/', views.cancelar_reserva, name='cancelar'),
    path('confirmar/<str:token>/', views.confirmar_reserva, name='confirmar'),

    # CRUD
    path('', views.ClienteListView.as_view(), name='cliente_list'),
    path('<str:token>/', views.ClienteDetailView.as_view(), name='cliente_detail'),
    path('crear/', views.ClienteCreateView.as_view(), name='cliente_create'),
    path('<str:token>/editar/', views.ClienteUpdateView.as_view(), name='cliente_update'),
    path('<str:token>/eliminar/', views.ClienteDeleteView.as_view(), name='cliente_delete'),

    # Otros
    path('editar-perfil/', views.editar_perfil, name='editar_perfil'),
    path('<str:token>/toggle-activo/', views.toggle_cliente_activo, name='cliente_toggle_activo'),
]