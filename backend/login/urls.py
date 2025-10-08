from django.urls import path
from . import views

app_name = 'login'

urlpatterns = [
    path("", views.login_view, name='login'),
    path("admin-panel/", views.admin_panel, name='admin_panel'), 
    path("dashboard/", views.dashboard, name='dashboard'),
    path("logout/", views.logout_view, name='logout'),
    path("update-user/", views.update_user, name='update_user'),  # <-- Nueva ruta
]