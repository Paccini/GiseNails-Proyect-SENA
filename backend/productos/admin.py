from django.contrib import admin
from .models import Producto

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'cantidad', 'precio', 'recomendado', 'en_uso', 'ventas')
    list_editable = ('recomendado', 'en_uso', 'ventas')
    search_fields = ('nombre', 'descripcion')
    list_filter = ('recomendado', 'en_uso')
