from django.shortcuts import redirect
from django.contrib.auth.forms import UserCreationForm

def register(request):
    print(UserCreationForm(request.POST))
    return redirect('/app/')
