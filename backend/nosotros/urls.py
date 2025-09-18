from django.urls import path
from nosotros import views
urlpatterns = [
    path("" , views.nosotros , name="nosotros" ),
]
