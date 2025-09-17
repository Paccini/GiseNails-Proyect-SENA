from django.shortcuts import render
from .models import Tarea
# from nosotros import views

# Create your views here.

def nosotros (request):
    tarea = Tarea.objects.all()
    context = {'tareas' : tarea}
    return render (request , 'todo/nosotros.html', context)