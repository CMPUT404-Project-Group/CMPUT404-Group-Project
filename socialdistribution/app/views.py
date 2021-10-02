from django.shortcuts import render

def index (request):
    return render(request, 'app/index.html')
    
def register(request):
    return render(request, 'app/register.html')
