from .forms import RegisterForm, PostCreationForm, CommentCreationForm, ManageProfileForm, SharePostForm
from api.models import User, Post, Node
import datetime
import json
import os
import requests
import time
from .forms import RegisterForm, PostCreationForm, CommentCreationForm, ManageProfileForm
from api.models import User, Post, Comment, Like, GithubAccessData
from api.serializers import PostSerializer, FriendRequestSerializer
from requests.models import Response
from rest_framework import serializers
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from friendship.models import Follow, Friend, FriendshipRequest
from django.urls import reverse
from dotenv import load_dotenv
import logging
from django.views import generic

from django.conf import settings
HOST_URL = settings.HOST_URL
HOST_API_URL = settings.HOST_API_URL
API_TOKEN = settings.API_TOKEN

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # https://www.youtube.com/watch?v=q4jPR-M0TAQ&list=PL-osiE80TeTtoQCKZ03TU5fNfx2UY6U4p&index=6
            # Will give a notification when register successfully
            displayName = form.cleaned_data.get('displayName')
            password = form.cleaned_data.get('password1')
            # messages.success(request, f'Request to register account {displayName} has been submitted!')
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
    #Get all posts from yourself (besides unlisted ones)
    user_posts = Post.objects.all().order_by('-published').filter(author=request.user, unlisted=False)

    #Get public posts of followers
    followed_qs = Follow.objects.filter(follower_id=request.user.id)
    followed_ids = [item.followee_id for item in followed_qs]
    follower_posts = Post.objects.all().filter(author__in=followed_ids, visibility="public", unlisted=False)

    #Get public and friends only posts from friends
    friends_qs = Friend.objects.friends(request.user)
    friends_ids = [item.id for item in friends_qs]

    friends_posts = Post.objects.all().filter(author__in=friends_ids, visibility="private_to_friend", unlisted=False)

    #Union of above post querysets, ordered by published date
    stream_posts_obj = (follower_posts | friends_posts | user_posts).distinct().order_by('-published')
    stream_posts = PostSerializer(stream_posts_obj, many=True).data
    
    for post in stream_posts:
            post_id = post['id']
            url = f'{HOST_URL}/app/posts/{post_id}'
            post['source'] = url
            post['origin'] = url

    context = {
        "stream_posts" : stream_posts
    }

    return render(request, 'app/index.html', context)

@login_required
def create_post(request):
    # https://stackoverflow.com/questions/43347566/how-to-pass-user-object-to-forms-in-django
    if request.method == 'POST':
        user = request.user
        form = PostCreationForm(data=request.POST, files=request.FILES, user=user)
        if form.is_valid():
            form.save()
            return redirect('app:index')
    else:
        form = PostCreationForm()

    return render(request, 'posts/create_post.html', {'form': form})

@login_required
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

@login_required
def share_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    context = {
        'post': post}
    if request.method == 'POST':
        user = request.user
        form = SharePostForm(data=request.POST, user=user, post=post)
        if form.is_valid():
            form.save()
            return redirect('app:index')
    else:
        form = SharePostForm()

    return render(request, 'posts/share_post.html', context)


def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    user = request.user

    is_author = post.author == user

    if not is_author:
        return HttpResponseForbidden()
    else:
        post.delete()
        return render(request, 'app/index.html')

@login_required
def post(request, post_id):
    post_obj = get_object_or_404(Post, pk=post_id)
    post = PostSerializer(post_obj).data
    user = request.user

    is_author = False
    if post_obj.author == user:
        is_author = True

    context = {
        'post': post,
        'is_author': is_author}

    if request.method == 'GET':
        if (request.GET.get('like-button')):
            like_post(request, post_id)
        return render(request, 'posts/view_post.html', context)

    elif request.method == 'POST':
        data = request.POST.dict()
        cookie = data.pop('csrfmiddlewaretoken')
        query_set = Post.objects.filter(id=post_id)

        posts_updated = query_set.update(**data)
        if posts_updated == 0:
            return HttpResponseBadRequest("Something unexpected has occured!")

        return redirect('app:index')

def view_post(request, post_id):
    post_obj = get_object_or_404(Post, pk=post_id)
    post = PostSerializer(post_obj).data
    if (post.shared_post != None):
        original_post_obj = get_object_or_404(Post, pk=post_obj.shared_post.post.id)
        original_post = PostSerializer(original_post_obj).data
        context = {
            'shared_post': post,
            'original_post': original_post}
        return render(request, 'posts/view_shared_post.html', context)
    else:
        context = {'post': post}
        return render(request, 'posts/view_post.html', context)

      
@login_required
def view_profile(request):
    user = request.user
    if request.GET.get('github-sync-button'):
        sync_github_activity(request)
    return render(request, 'profile/view_profile.html', {'user': user})
    
@login_required
def view_other_user(request, other_user_id):
    if User.objects.filter(id=other_user_id).exists():
        other_user = User.objects.get(id=other_user_id)
    else:
        for node in Node.objects.get_queryset():
            url = str(node) + 'author/' + other_user_id
            res = requests.get(url, headers={})
            if (res.status_code==200):
                break
        other_user = json.loads(res.content.decode('utf-8'))['data'][0]
        print(other_user)
        return render(request, 'profile/view_other_user.html', {'other_user': other_user})

    if other_user==request.user: 
        return redirect('app:view-profile')

    if Friend.objects.are_friends(request.user, other_user):  
        # friends (follow each other)
        return render(request, 'profile/view_friend.html', {'other_user': other_user})
    elif Follow.objects.follows(request.user, other_user):   
        # following
        return render(request, 'profile/view_following_user.html', {'other_user': other_user})
    else:  # not following
        return render(request, 'profile/view_other_user.html', {'other_user': other_user})


@login_required
def view_followers(request):
    user = request.user
    url = HOST_API_URL + 'author/%s/followers/' % user.id
    res = requests.get(url)
    data = json.loads(res.content.decode('utf-8'))
    return render(request, 'profile/view_followers.html', {'data': data.get('items')})

@login_required
def explore_authors(request):
    # get local authors
    headers = {'Authorization': 'Token %s' % API_TOKEN}
    res = requests.get(HOST_URL+reverse('api:authors'), headers=headers)
    data = json.loads(res.content.decode('utf-8'))
    local_authors = data.get('data')
    for author in local_authors:
        if author.get('displayName') == request.user.displayName: # remove current user from list
            local_authors.remove(author)
    
    # get remote authors
    nodes = Node.objects.get_queryset()
    for node in nodes:
        res = requests.get(str(node)+'authors/', headers={})
        remote_authors = json.loads(res.content.decode('utf-8'))['data']
    return render(request, 'app/explore-authors.html', {'local_authors': local_authors, 'remote_authors': remote_authors })


@login_required
def manage_profile(request):
    if request.method == 'POST':
        form = ManageProfileForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()
            # Will give a notification when edit successfully
            messages.success(request,f'Request to edit profile has been submitted!')

            return redirect('app:view-profile')
       
    else:
        form = ManageProfileForm(instance=request.user)
    return render(request, 'profile/manage_profile.html', {'form': form})

@login_required
def follow(request, other_user_id):
    if request.method == 'POST':
        other_user = User.objects.get(id=other_user_id)

        try: 
            # send a friend request
            friend_request = Friend.objects.add_friend(
            request.user,                              # The sender
            other_user)                                # The recipient

            # send request to object user's inbox
            serializer = FriendRequestSerializer(friend_request).data
            inboxURL = serializer.get('object', {}).get('url') + '/inbox/'
            requests.post(inboxURL, json=serializer)

            Follow.objects.add_follower(request.user, other_user)  # follow
            messages.success(request,f'Your friend request has been sent!')

        except:
            # if there's already a request from other_user
            if (FriendshipRequest.objects.filter(from_user=other_user, to_user=request.user).exists() ):
                # accept friend request from other_user
                friend_request = FriendshipRequest.objects.get(from_user=other_user, to_user=request.user)
                friend_request.accept()
                Follow.objects.add_follower(request.user, other_user)  # follow
                messages.success(request,f'You and %s are friends now!' % other_user.displayName)
            elif (FriendshipRequest.objects.filter(from_user=request.user, to_user=other_user).exists()):
                Follow.objects.add_follower(request.user, other_user)  # follow
                messages.info(request,f'You already sent a friend request ')
            else: 
                messages.info(request,f'Error')        
        return redirect('app:view-other-user', other_user_id=other_user_id)

@login_required
def unfollow(request, other_user_id):
    if request.method == 'POST':
        other_user = User.objects.get(id=other_user_id)
        Follow.objects.remove_follower(request.user, other_user)  # unfollow 

        # remove friend if user & other_user are friends
        if Friend.objects.are_friends(request.user, other_user):
            Friend.objects.remove_friend(request.user, other_user )

        return redirect('app:view-other-user', other_user_id=other_user_id)

@login_required
def create_comment(request, post_id):
    if request.method == 'POST':
        user = request.user
        post = get_object_or_404(Post, pk=post_id)
        form = CommentCreationForm(data=request.POST, user=user, post=post)
        if form.is_valid():
            form.save()
            post.count += 1
            post.save()
            return redirect('app:index')
    else:
        form = CommentCreationForm()

    return render(request, 'comments/create_comment.html', {'form': form})

def comments(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comments = Comment.objects.all().filter(post=post)

    context = {
        'comments': comments,
        'post_id': post_id
    }

    if (request.GET.get('like-button')):
        like_comment(request, request.GET.get('like-button'))

    # Only public posts have comments that are visible to other users
    if (post.visibility != "public" and post.author != request.user):
        return HttpResponseForbidden()
    else:
        return render(request, "comments/comments.html", context)

@login_required
def like_post(request, post_id):
    user = request.user
    post = get_object_or_404(Post, pk=post_id)

    like = Like.objects.create_like(
        author=user,
        content_object=post
    )

@login_required
def like_comment(request, comment_id):
    user = request.user
    comment = get_object_or_404(Comment, pk=comment_id)

    like = Like.objects.create_like(
        author=user,
        content_object=comment
    )

@login_required
def inbox(request, author_id):
    url = HOST_URL+reverse('api:inbox', kwargs={'author_id': author_id})
    print(url)
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


class PostListView(generic.ListView):
    model = Post
    template_name = 'posts/post_list.html'
    
    def get(self, request):
        queryset = Post.objects.filter(visibility="public", unlisted=False)[:20]
        serializer = PostSerializer(queryset, many=True)

        for post in serializer.data:
            post_id = post['id']
            url = f'{HOST_URL}/app/posts/{post_id}'
            post['source'] = url
            post['origin'] = url
        
        return render(request, self.template_name, {'post_list': serializer.data})
      
@login_required
def sync_github_activity(request):
    user = request.user
    if user.github:
        github_username = user.github

        uri = f"https://api.github.com/users/{github_username}/events"
        http_response = requests.get(uri)
        response_json = http_response.json()

        try:
            github_access_data = GithubAccessData.objects.get(user_id=user.id)
        except GithubAccessData.DoesNotExist:
            last_accessed_date = None
            github_access_data = GithubAccessData.objects.create(
                user=user
            )
        else:
            last_accessed_date = github_access_data.last_accessed
            github_access_data.last_accessed = datetime.datetime.now()
            github_access_data.save()
            
        
        for event in response_json:
            creation_date = time.strptime(event['created_at'], "%Y-%m-%dT%H:%M:%SZ")
            event_creation_datetime = datetime.datetime(
                creation_date.tm_year, 
                creation_date.tm_mon,
                creation_date.tm_mday,
                creation_date.tm_hour,
                creation_date.tm_min,
                creation_date.tm_sec,
                tzinfo=datetime.timezone.utc)
            if not last_accessed_date or event_creation_datetime > last_accessed_date:
                github_event_to_post_adapter(user, event)
    
    


def github_event_to_post_adapter(author, event):
    type = Post.ContentType.PLAIN
    title = f"Github Event of type {event['type']}"
    categories = f"github, {event['type']}"
    text_content = f"""
    id: {str(event['id'])}\n
    repository: {str(event['repo'])}\n
    Payload: {str(event['payload'])}\n"""


    post = Post.objects.create_post(
        author=author, 
        categories=categories,
        image_content=None,
        text_content=text_content,
        title=title,
        visibility=Post.Visibility.PUBLIC,
        unlisted=False,
        )
            