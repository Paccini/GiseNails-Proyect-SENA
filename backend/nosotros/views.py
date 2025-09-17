from django.shortcuts import render
# from nosotros import views

# Create your views here.
def nosotros(request):
    return render(request, 'nosotros/nosotros.html')