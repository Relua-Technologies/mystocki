
from django.contrib.auth import logout
from django.shortcuts import redirect

def signout_view(request):
    logout(request)
    return redirect('sign_in')