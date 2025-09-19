from django.shortcuts import render
# from nosotros import views

# Create your views here.
def index(request):
    return render(request, 'inicio/index.html')