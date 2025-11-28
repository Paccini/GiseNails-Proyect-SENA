from django.urls import path
from . import views

app_name = 'login'

urlpatterns = [
    path("", views.login_view, name='login'),
    path("admin-panel/", views.admin_panel, name='admin_panel'), 
    path("dashboard/", views.dashboard, name='dashboard'),
    path("logout/", views.logout_view, name='logout'),
    path('registro/', views.registro_cliente, name='registro'),
    path("update-user/", views.update_user, name='update_user'),  # <-- Nueva ruta
    path("password-reset/", views.password_reset_view, name='password_reset'),
    path("password-reset-confirm/<str:token>/", views.password_reset_confirm_view, name='password_reset_confirm'),
]