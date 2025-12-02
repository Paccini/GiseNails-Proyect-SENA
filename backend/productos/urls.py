from django.urls import path
from . import views

app_name = 'producto'

urlpatterns = [
    path('', views.producto_list, name='producto_list'),
    path('producto/', views.lista_productos, name='lista_productos'),
    path('crear/', views.producto_create, name='producto_create'),
    path('<path:token>/editar/', views.producto_update, name='producto_update'),
    path('<path:token>/eliminar/', views.producto_delete, name='producto_delete'),
    path('<path:token>/', views.producto_detail, name='producto_detail'),
]