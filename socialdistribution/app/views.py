from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required

from api.models import User, Post
from .forms import RegisterForm, PostCreationForm

@login_required
def index (request):
    return render(request, 'app/index.html')
    
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('app:index')
    else:
        form = RegisterForm()
    return render(request, 'app/register.html', {'form': form})

def create_post(request):
    if request.method == 'POST':
        form = Post_Creation_Form(request.POST)
        user = request.user.id
        print(user)
        if form.is_valid():
            return redirect('app:index')
    else:
        form = Post_Creation_Form()
    return render(request, 'posts/create_post.html', {'form': form})