from django.urls import path
from .views import (
    reserva, horarios_disponibles,
    home, agregar_reserva, editar_reserva, eliminar_reserva, ReservaCreateView,
    completar_reserva, exportar_facturacion_excel
)
from . import views

app_name = 'reserva'

urlpatterns = [
    path('', reserva, name='reserva'),  # Ruta /reserva/
    path('horarios-disponibles/', horarios_disponibles, name='horarios_disponibles'),

    # Rutas administrativas de reservas
    path('reservas/', home, name='home'),
    path('reservas/agregar/', ReservaCreateView.as_view(), name='agregar_reserva'),
    path('reservas/editar/<str:token>/', editar_reserva, name='editar_reserva'),
    path('reservas/eliminar/<str:token>/', eliminar_reserva, name='eliminar_reserva'),
    path('completar-reserva/', completar_reserva, name='completar_reserva'),

    # Otras rutas
    path('facturacion/', views.facturacion, name='facturacion'),

    # Nueva ruta para pago en efectivo
    path('factura/<str:token>/pago-efectivo/', views.pago_efectivo_admin, name='pago_efectivo_admin'),

    # Nueva ruta para la API de búsqueda de factura
    path('api/buscar-factura/', views.api_buscar_factura, name='api_buscar_factura'),

    # Ruta para exportar facturación a Excel
    path('exportar-facturacion-excel/', exportar_facturacion_excel, name='exportar_facturacion_excel'),
]
