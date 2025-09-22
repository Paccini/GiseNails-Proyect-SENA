
from django.urls import path

from . import views

app_name = 'producto'
urlpatterns = [
	path('producto/', views.lista_productos, name='lista_productos'),
	
]





