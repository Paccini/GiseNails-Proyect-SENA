from django.shortcuts import redirect

def csrf_failure(request, reason=""):
    return redirect('login:login')