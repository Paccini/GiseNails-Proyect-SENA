from django.shortcuts import redirect, render

def csrf_failure(request, reason=""):
    return redirect('login:login')

def home(request):
    return render(request, 'home.html')  # Asegúrate de tener este template

def panel_admin(request):
    # Vista para admin
    return render(request, 'admin/panel.html')