from django.urls import path
from . import views

app_name = 'clientes'

urlpatterns = [
    path('registro/', views.registro_cliente, name='registro'),
    path('panel/', views.panel_cliente, name='panel'),
    path('agendar/', views.agendar_reserva, name='agendar'),  # Cambiado a reserva
    path('cancelar/<int:pk>/', views.cancelar_reserva, name='cancelar'),  # Cambiado a reserva

    # CRUD para clientes (administrador)
    path('', views.ClienteListView.as_view(), name='cliente_list'),
    path('<int:pk>/', views.ClienteDetailView.as_view(), name='cliente_detail'),
    path('crear/', views.ClienteCreateView.as_view(), name='cliente_create'),
    path('<int:pk>/editar/', views.ClienteUpdateView.as_view(), name='cliente_update'),
    path('<int:pk>/eliminar/', views.ClienteDeleteView.as_view(), name='cliente_delete'),
]