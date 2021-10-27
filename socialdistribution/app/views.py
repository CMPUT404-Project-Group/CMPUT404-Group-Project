import json
import os

import requests
from requests.models import Response
from api.models import Post
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse, HttpResponseForbidden, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import authenticate, login
from django.urls import reverse
from dotenv import load_dotenv
from .forms import (CommentCreationForm, ManageProfileForm, PostCreationForm,
                    RegisterForm)

@login_required
def index(request):
    stream_posts = Post.objects.all().order_by('-published').filter(author=request.user)

    context = {
        "stream_posts" : stream_posts
    }


    return render(request, 'app/index.html', context)
load_dotenv()
HOST_URL = os.getenv("HOST_URL")

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # https://www.youtube.com/watch?v=q4jPR-M0TAQ&list=PL-osiE80TeTtoQCKZ03TU5fNfx2UY6U4p&index=6
            # Will give a notification when register successfully
            displayName = form.cleaned_data.get('displayName')
            password = form.cleaned_data.get('password1')
            messages.success(
                request, f'Request to register account {displayName} has been submitted!')
            form.save()
            user = authenticate(
                request, displayName=displayName, password=password)
            if user is not None:
                login(request, user)
            return redirect('app:index')
    else:
        form = RegisterForm()
    return render(request, 'app/register.html', {'form': form})


@login_required
def index(request):
    return render(request, 'app/index.html')


@login_required
def create_post(request):
    # https://stackoverflow.com/questions/43347566/how-to-pass-user-object-to-forms-in-django
    if request.method == 'POST':
        user = request.user
        form = PostCreationForm(data=request.POST, user=user)
        if form.is_valid():
            form.save()
            return redirect('app:index')
    else:
        form = PostCreationForm()

    return render(request, 'posts/create_post.html', {'form': form})


def edit_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    user = request.user
    is_author = False

    context = {'post': post}

    if post.author == user:
        is_author = True

    if not is_author:
        return HttpResponseForbidden()
    else:
        return render(request, 'posts/edit_post.html', context)

def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    user = request.user

    is_author = post.author == user

    if not is_author:
        return HttpResponseForbidden()
    else:
        post.delete()
        return render(request, 'app/index.html')

def post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    user = request.user

    is_author = False
    if post.author == user:
        is_author = True

    context = {
        'post': post,
        'is_author': is_author}

    if request.method == 'GET':
        return render(request, 'posts/view_post.html', context)

    elif request.method == 'POST':
        form = PostCreationForm(
            data=request.POST, user=user, id=post_id, published=post.published)
        if form.is_valid():
            form.save()

        return redirect('app:index')


def view_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    context = {'post': post}

    return render(request, 'posts/view_post.html', context)


def view_profile(request):
    user = request.user
    return render(request, 'profile/view_profile.html', {'user': user})


def manage_profile(request):
    if request.method == 'POST':
        form = ManageProfileForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()

            # https://www.youtube.com/watch?v=q4jPR-M0TAQ&list=PL-osiE80TeTtoQCKZ03TU5fNfx2UY6U4p&index=6
            # Will give a notification when edit successfully
            messages.success(
                request, f'Request to edit profile has been submitted!')
            return redirect('app:view-profile')
       
    else:
        form = ManageProfileForm(instance=request.user)

        return render(request, 'profile/manage_profile.html', {'form': form})


@login_required
def create_comment(request, post_id):
    if request.method == 'POST':
        user = request.user
        post = get_object_or_404(Post, pk=post_id)
        form = CommentCreationForm(data=request.POST, user=user, post=post)
        if form.is_valid():
            form.save()
            return redirect('app:index')
    else:
        form = CommentCreationForm()

    return render(request, 'comments/create_comment.html', {'form': form})

@login_required
def inbox(request, author_id):
    url = HOST_URL+reverse('api:inbox', kwargs={'author_id': author_id})
    if request.method == 'GET':
        try:
            page = request.GET.get('page')
            size = request.GET.get('size')
        except:
            page = 1
            size = None

        if page:
            url += '?page=%s' % page
        if size:
            url += '&size=%s' % size

        req = requests.get(url)
        res = json.loads(req.content.decode('utf-8'))
        res['author'] = request.path.split('/')[3]
        return render(request, 'app/inbox.html', {'res': res})
    elif request.method == "DELETE":
        req = requests.delete(url)
        return HttpResponse(status=req.status_code)
    else:
        return HttpResponseNotAllowed
