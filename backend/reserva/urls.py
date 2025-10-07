from django.urls import path
from .views import reserva, horarios_disponibles, completar_reserva

urlpatterns = [
    path('', reserva, name='reserva'),  # Esta línea crea la ruta /reserva/
    path('horarios-disponibles/', horarios_disponibles, name='horarios_disponibles'),
    path('completar-reserva/', completar_reserva, name='completar_reserva'),
    # ... otras rutas ...
]