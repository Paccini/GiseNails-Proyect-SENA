from django.urls import path
from reserva import views
urlpatterns = [
    path("" , views.reserva , name="reserva" ),
]