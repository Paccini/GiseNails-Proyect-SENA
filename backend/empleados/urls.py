from django.urls import path
from . import views

urlpatterns = [
    path('', views.empleado_list, name='empleado_list'),
    path('crear/', views.empleado_create, name='empleado_create'),
    path('<int:pk>/editar/', views.empleado_update, name='empleado_update'),
    path('<int:pk>/eliminar/', views.empleado_delete, name='empleado_delete'),
    path('panel/', views.panel_empleado, name='panel_empleado'),
    path('cita/<int:pk>/editar/', views.editar_cita_empleado, name='editar_cita_empleado'),
    path('horas-disponibles/', views.horas_disponibles_empleado, name='horas_disponibles_empleado'),
    path('agendar-cita/', views.agendar_cita_empleado, name='agendar_cita_empleado'),
    path('<int:pk>/toggle-activo/', views.toggle_empleado_activo, name='empleado_toggle_activo'),
]