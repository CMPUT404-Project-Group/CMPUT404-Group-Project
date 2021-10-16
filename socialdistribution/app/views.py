from django.http.response import HttpResponse
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
    #https://stackoverflow.com/questions/43347566/how-to-pass-user-object-to-forms-in-django
    if request.method == 'POST':
        user = request.user
        form = PostCreationForm(data=request.POST, user=user)
        if form.is_valid():
            form.save()
            return redirect('app:index')
        else:
            print("INVALID FORM")
    else:
        form = PostCreationForm()
        
    return render(request, 'posts/create_post.html', {'form': form})

def view_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    return HttpResponse(post)
    