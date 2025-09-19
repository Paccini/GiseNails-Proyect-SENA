from django.urls import path
from reserva import views
urlpatterns = [
    path("", views.reserva, name="reserva"),
    path('nueva/', views.reserva2, name='reserva2'),
    # path('horarios-disponibles/', views.horarios_disponibles, name='horarios_disponibles'),
]