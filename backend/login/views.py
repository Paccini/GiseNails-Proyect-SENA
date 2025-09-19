from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.cache import never_cache
from .forms import LoginForm
from clientes.models import Cliente

def login_view(request):
    return render(request, 'login/login.html')
# def login_view(request):
#     if request.user.is_authenticated and request.user.is_staff:
#         return redirect('login:inicio')
#     form = LoginForm(request.POST or None)
#     if request.method == 'POST' and form.is_valid():
#         username = form.cleaned_data['username']
#         password = form.cleaned_data['password']
#         user = authenticate(request, username=username, password=password)
#         if user is not None:
#             login(request, user)
#             if user.is_staff:
#                 return redirect('dashboard')
#             elif Cliente.objects.filter(user=user).exists():
#                 return redirect('clientes:panel')
#             else:
#                 return redirect('dashboard')
#         else:
#             form.add_error(None, 'Usuario o contraseña incorrectos')
#     return render(request, 'login/login.html', {'form': form})

# @never_cache
# def logout_view(request):
#     logout(request)
#     return redirect('login:login')

# @login_required
# @user_passes_test(lambda u: u.is_staff)
# @never_cache
# def inicio(request):
#     return render(request, 'index.html')