

from django.urls import path
from . import views

app_name = 'servicio'
urlpatterns = [
    path('servicio/', views.lista_servicios, name='lista_servicios'),
    path('', views.servicio_list, name='servicio_list'),
    path('crear/', views.servicio_create, name='servicio_create'),
    path('<int:pk>/editar/', views.servicio_update, name='servicio_update'),
    path('<int:pk>/eliminar/', views.servicio_delete, name='servicio_delete'),
    path('<int:pk>/', views.servicio_detail, name='servicio_detail'),  # <-- Agrega esta línea
]

