from django.urls import path
from . import views

app_name = 'login'

urlpatterns = [
    path("", views.login_view, name='login'),
    path("admin-panel/", views.admin_panel, name='admin_panel'), 
    path("logout/", views.logout_view, name='logout'), # <-- Nueva ruta
]