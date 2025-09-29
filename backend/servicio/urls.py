

from django.urls import path
from . import views

app_name = 'servicio'
urlpatterns = [
    path('servicio/', views.lista_servicios, name='lista_servicios'),
    
]

