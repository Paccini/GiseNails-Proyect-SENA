from django.urls import path
from . import views

urlpatterns = [
    path('', views.empleado_list, name='empleado_list'),
    path('crear/', views.empleado_create, name='empleado_create'),
    path('<int:pk>/editar/', views.empleado_update, name='empleado_update'),
    path('<int:pk>/eliminar/', views.empleado_delete, name='empleado_delete'),
]