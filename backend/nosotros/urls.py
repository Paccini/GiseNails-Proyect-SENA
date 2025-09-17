from django.contrib import admin
from django.urls import path
from nosotros import views
urlpatterns = [
    path("nosotros/" , views.nosotros , name="nosotros" ),
]
