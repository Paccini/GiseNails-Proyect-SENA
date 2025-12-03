from django.urls import path
from . import views
from .views import cambiar_estado_cita_empleado

urlpatterns = [
    path('', views.empleado_list, name='empleado_list'),
    path('crear/', views.empleado_create, name='empleado_create'),
    path('<str:token>/editar/', views.empleado_update, name='empleado_update'),
    path('<str:token>/eliminar/', views.empleado_delete, name='empleado_delete'),
    path('panel/', views.panel_empleado, name='panel_empleado'),
    path('cita/<str:token>/editar/', views.editar_cita_empleado, name='editar_cita_empleado'),
    path('horas-disponibles/', views.horas_disponibles_empleado, name='horas_disponibles_empleado'),
    path('agendar-cita/', views.agendar_cita_empleado, name='agendar_cita_empleado'),
    path('<str:token>/toggle-activo/', views.toggle_empleado_activo, name='empleado_toggle_activo'),
    path('cita/<int:pk>/cambiar-estado/', cambiar_estado_cita_empleado, name='cambiar_estado_cita_empleado'),
]