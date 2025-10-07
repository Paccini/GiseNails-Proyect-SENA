from django.contrib import admin
from .models import Servicio

class ServicioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio')  # Quita 'destacado'

admin.site.register(Servicio, ServicioAdmin)
