from django.shortcuts import render
# from reserva import views
# Create your views here.
def reserva(request):
    return render(request, 'reserva/reserva.html')