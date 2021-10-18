from .forms import RegisterForm, PostCreationForm
from api.models import User, Post
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
import logging

@login_required
def index (request):
    return render(request, 'app/index.html')
    
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # https://www.youtube.com/watch?v=q4jPR-M0TAQ&list=PL-osiE80TeTtoQCKZ03TU5fNfx2UY6U4p&index=6 
            # Will give a notification when register successfully 
            username = form.cleaned_data.get('username')
            messages.success(request,f'Request to register account {username} has been submitted!')
            form.save()
            return redirect('app:index')
    else:
        form = RegisterForm()
    return render(request, 'app/register.html', {'form': form})

def create_post(request):
    #https://stackoverflow.com/questions/43347566/how-to-pass-user-object-to-forms-in-django
    if request.method == 'POST':
        user = request.user
        form = PostCreationForm(data=request.POST, files=request.FILES, user=user)
        if form.is_valid():
            form.save()
            return redirect('app:index')
        else:
            print("INVALID FORM")
    else:
        form = PostCreationForm()
        
    return render(request, 'posts/create_post.html', {'form': form})

def view_post(request, post_id):
    context = {}
    post = get_object_or_404(Post, pk=post_id)
    context['post'] = post
    return render(request, 'posts/view_post.html', context)
    