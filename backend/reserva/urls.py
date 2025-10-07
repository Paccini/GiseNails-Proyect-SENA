from django.urls import path
from .views import (
    reserva, horarios_disponibles,
    home, agregar_reserva, editar_reserva, eliminar_reserva, ReservaCreateView
)

app_name = 'reserva'

urlpatterns = [
    path('', reserva, name='reserva'),  # Ruta /reserva/
    path('horarios-disponibles/', horarios_disponibles, name='horarios_disponibles'),

    # Rutas administrativas de reservas
    path('reservas/', home, name='home'),
    path('reservas/agregar/', ReservaCreateView.as_view(), name='agregar_reserva'),
    path('reservas/editar/<int:pk>/', editar_reserva, name='editar_reserva'),
    path('reservas/eliminar/<int:pk>/', eliminar_reserva, name='eliminar_reserva'),
]