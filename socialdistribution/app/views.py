from .forms import RegisterForm, PostCreationForm
from api.models import User, Post
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import authenticate, login
from django.views import generic


@login_required
def index(request):
    return render(request, 'app/index.html')


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


def create_post(request):
    # https://stackoverflow.com/questions/43347566/how-to-pass-user-object-to-forms-in-django
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


class PostListView(generic.ListView):
    model = Post
    template_name = 'posts/post_list.html'

    def get_queryset(self):
        return Post.objects.filter(visibility="public", unlisted=0)
