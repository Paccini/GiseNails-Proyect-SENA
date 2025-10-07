from django.urls import path
from .views import reserva, horarios_disponibles

urlpatterns = [
    path('', reserva, name='reserva'),  # Esta línea crea la ruta /reserva/
    path('horarios-disponibles/', horarios_disponibles, name='horarios_disponibles'),
    # ... otras rutas ...
]