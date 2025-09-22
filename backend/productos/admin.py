from django.contrib import admin
from .models import Producto

class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'cantidad', 'precio')  # Quita 'destacado'

admin.site.register(Producto, ProductoAdmin)
