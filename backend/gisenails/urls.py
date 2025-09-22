"""
URL configuration for gisenails project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('inicio.urls')),
    path('nosotros/', include('nosotros.urls')),
    path('reserva/', include(('reserva.urls', 'reserva'), namespace='reserva')),
    path('servicio/', include(('servicio.urls', 'servicio'), namespace='servicio')),
    path('productos/', include(('productos.urls', 'productos'), namespace='productos')),
    path('login/', include('login.urls')),
    path('clientes/', include(('clientes.urls', 'clientes'), namespace='clientes')),
    path('paneladmin/', views.panel_admin, name='paneladmin'),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


