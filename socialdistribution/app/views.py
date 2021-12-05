from uuid import uuid4
from requests import api

from .forms import RegisterForm, PostCreationForm, CommentCreationForm, ManageProfileForm, SharePostForm
from api.models import User, Post, Node
from src.url_decorator import URLDecorator
from src.Node import Node_Interface_Factory, Abstract_Node_Interface
import datetime
import json
import os
import requests
import time
from .forms import RegisterForm, PostCreationForm, CommentCreationForm, ManageProfileForm
from api.models import User, Post, Comment, Like, GithubAccessData
from api.serializers import PostSerializer, FriendRequestSerializer, ForeignFriendRequestSerializer
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
from rest_framework.authtoken.models import Token
import base64
from django.conf import settings
HOST_URL = settings.HOST_URL
HOST_API_URL = settings.HOST_API_URL
API_TOKEN = settings.API_TOKEN
TEAM_12_TOKEN = settings.TEAM_12_TOKEN
TEAM_18_TOKEN = settings.TEAM_18_TOKEN
TEAM_02_TOKEN = settings.TEAM_02_TOKEN


def register(request):
    """
    Form for new users to register. If request is POST, we use the default django auth to create the user.
    """
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
    """
    Home page for a logged in and authenticated user.

    Renders the user's "stream", pulling in all of the public and user's own posts.
    """
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
            post_id = post['id'].split('/')[-1]
            post['id'] = post_id
            url = f'{HOST_URL}/app/posts/{post_id}'
            post['source'] = url
            post['origin'] = url

    context = {
        "stream_posts" : stream_posts
    }

    return render(request, 'app/index.html', context)

@login_required
def create_post(request):
    """
    From to create a new post. Uses the PostCreationForm. 
    
    If the post is succesfully created, redirects to the user's stream.
    """
    # https://stackoverflow.com/questions/43347566/how-to-pass-user-object-to-forms-in-django
    if request.method == 'POST':
        user = request.user
        form = PostCreationForm(data=request.POST, files=request.FILES, user=user)
        if form.is_valid():
            form.save()
            return redirect('app:index')
    else:
        form = PostCreationForm()
    node = Node.objects.get(team="LOCAL")
    node_interface = Node_Interface_Factory.get_interface(node)
    friends = node_interface.get_followers(node, request.user.url)
    for friend in friends:
        # get the auth token
        token = Node.objects.get(url=friend['host']).auth_token
        friend['token'] = token
    return render(request, 'posts/create_post.html', {'form': form, 'friends': friends, 'token': API_TOKEN})

@login_required
def edit_post(request, post_id):
    """
    Renders a form with the post data given by post_id.

    Only an author can edit their own post, otherwise it returns a 403.
    """
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
    """
    From to allow a user to share another user's post given by post_id.
    """
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
    """
    Allows the user to delete the post given by post_id.

    Only an author can edit their own post, otherwise it returns a 403.
    """
    post = get_object_or_404(Post, pk=post_id)
    user = request.user

    is_author = post.author == user

    if not is_author:
        return HttpResponseForbidden()
    else:
        post.delete()
        return redirect('app:index')

@login_required
def post(request, post_id):
    """
    Allows the user to view the details of the post given by post_id.

    It only displays posts that are public and listed, otherwise it returns 403.
    """
    post_obj = get_object_or_404(Post, pk=post_id)
    post = PostSerializer(post_obj).data
    post['id'] = post['id'].split('/')[-1]
    user = request.user
    post_author = post_obj.author

    is_author = False
    if post_author == user:
        is_author = True

    context = {
        'post': post,
        'is_author': is_author}

    if request.method == 'GET':
        if (request.GET.get('like-button')):
            like_post(request, post_id)
        if (post_obj.visibility == 'private_to_author' and not is_author):
            return HttpResponseForbidden()
        elif (post_obj.visibility == 'private_to_friend' and not (is_author or Friend.objects.are_friends(request.user, post_author))):
            return HttpResponseForbidden()
        return render(request, 'posts/view_post.html', context)

    elif request.method == 'POST':
        data = request.POST.dict()
        cookie = data.pop('csrfmiddlewaretoken')
        query_set = Post.objects.filter(id=post_id)

        posts_updated = query_set.update(**data)
        if posts_updated == 0:
            return HttpResponseBadRequest("Something unexpected has occured!")

        return redirect('app:index')

@login_required
def foreign_post(request):
    """
    Allows users to view posts from foreign servers.

    This is different to local posts to handle with the origin urls, commenting, liking, etc.
    """
    data = request.POST.dict()
    if request.method == 'POST':
        url = data['post'].split('/author')[0]
        node = Node.objects.get(url=url)
        node_interface = Node_Interface_Factory.get_interface(node)
        post = node_interface.get_post(node, data['post'])
        request.session['foreign_post'] = post
    elif ('foreign_post' in request.session.keys()):
        post = request.session['foreign_post']
        node = Node.objects.get(url__contains=post['author']['host'])
        node_interface = Node_Interface_Factory.get_interface(node)
        
    context = {
        'post': post,
        'is_author': False,
        'user' : request.user,
        'token' : node.auth_token
    }

    return render(request, 'posts/view_foreign_post.html', context)

      
@login_required
def view_profile(request):
    """
    Allows user to view their own profile details.

    If the github-sync-button is pressed, it will trigger the sync_github_activity view to 
    pull the users github activity into thier stream.
    """
    user = request.user
    if request.GET.get('github-sync-button'):
        sync_github_activity(request)
    return render(request, 'profile/view_profile.html', {'user': user})
    
@login_required
def view_other_user(request, other_user_id):
    """
    Allows the user to view another users profile, and send them follow/friend requests.

    Depending on what the relationship is between the user and other_user_id, different
    templates will be rendered.
    """
    if User.objects.filter(id=other_user_id).exists():
        other_user = User.objects.get(id=other_user_id)
    else:
        for node in Node.objects.get_queryset().filter(is_active=True):
            node_interface = Node_Interface_Factory.get_interface(node)
            author = node_interface.get_author(node, other_user_id)
            if len(author) > 0:
                return render(request, 'profile/view_other_user.html', {'other_user': author})
        return render(HttpResponse('User not found'))
        

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
    """
    Allows the user to view all of the other users that are following them, and will receive their posts.
    """
    headers = {'Authorization': 'Basic %s' % API_TOKEN}
    user = request.user
    url = HOST_API_URL + 'author/%s/followers/' % user.id
    res = requests.get(url, headers=headers)
    data = json.loads(res.content.decode('utf-8'))
    return render(request, 'profile/view_followers.html', {'data': data.get('data')})

@login_required
def explore_authors(request):
    """
    Allows the user to view all of the authors (local and foreign) that are available for them to follow and view.
    """
    data = dict()
    # get local authors
    headers = {'Authorization': 'Basic %s' % API_TOKEN}
    res = requests.get(HOST_URL+reverse('api:authors'), headers=headers)
    data = json.loads(res.content.decode('utf-8'))
    local_authors = data.get('data')
    for author in local_authors:
        if author.get('displayName') == request.user.displayName: # remove current user from list
            local_authors.remove(author)
    data['local_authors'] = local_authors

    # get remote authors
    nodes = Node.objects.get_queryset().filter(is_active=True)
    remote_authors = dict()
    for node in nodes:
        node_interface = Node_Interface_Factory.get_interface(node)
        node_authors = node_interface.get_authors(node)
        remote_authors[node.team] = node_authors
        
    return render(request, 'app/explore-authors.html', {'local_authors': local_authors, 'remote_authors': remote_authors })


@login_required
def manage_profile(request):
    """
    Allows the user to edit and update thier profile information.
    """
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
    """
    A view that creates new friendship relationships between users.

    If they are sending other_user_id a friend request, it posts the follow
    object to the other user's inbox.
    """
    if request.method == 'POST':
        other_user = User.objects.get(id=other_user_id)
        headers = {'Authorization': 'Basic %s' % API_TOKEN}

        if other_user.type == 'foreign-author': 
            host = other_user.url.split('/')[2]
            if host == 'glowing-palm-tree1.herokuapp.com':
                token = TEAM_12_TOKEN
            elif host == 'cmput404-socialdistributio-t18.herokuapp.com':
                token = TEAM_18_TOKEN
            elif host == 'ourbackend.herokuapp.com':
                token = TEAM_02_TOKEN
            
            headers = {'Authorization': 'Basic %s' % token}

        try: 
            # send a friend request
            friend_request = Friend.objects.add_friend(
            request.user,                              # The sender
            other_user)                                # The recipient

            # send request to object user's inbox
            serializer = FriendRequestSerializer(friend_request).data
            inboxURL = serializer.get('object', {}).get('url') + '/inbox/'
            requests.post(inboxURL, json=serializer, headers=headers)

            Follow.objects.add_follower(request.user, other_user)  # follow
            messages.success(request,f'Your friend request has been sent!')

        except:
            # if there's already a request from other_user
            if (FriendshipRequest.objects.filter(from_user=other_user, to_user=request.user).exists() ):
                # accept friend request from other_user
                friend_request = FriendshipRequest.objects.get(from_user=other_user, to_user=request.user)
                friend_request.accept()
                Follow.objects.add_follower(request.user, other_user)  # follow

                # if other_user is foreign_user, send request to inbox
                if other_user.type == 'foreign-author':
                    instance = {'from_user':request.user.id, 'to_user':other_user_id}      
                    serializer = ForeignFriendRequestSerializer(instance).follow()
                    inboxURL = other_user.url + '/inbox/'
                    requests.post(inboxURL, json=serializer, headers=headers)

                messages.success(request,f'You and %s are friends now!' % other_user.displayName)
            elif (FriendshipRequest.objects.filter(from_user=request.user, to_user=other_user).exists()):
                Follow.objects.add_follower(request.user, other_user)  # follow
                messages.info(request,f'You already sent a friend request ')
            else: 
                messages.info(request,f'Error')        
        return redirect('app:view-other-user', other_user_id=other_user_id)

@login_required
def unfollow(request, other_user_id):
    """
    Allows the user to unfollow the user given by other_user_id.
    """
    if request.method == 'POST':
        other_user = User.objects.get(id=other_user_id)
        Follow.objects.remove_follower(request.user, other_user)  # unfollow 

        # remove friend if user & other_user are friends
        if Friend.objects.are_friends(request.user, other_user):
            Friend.objects.remove_friend(request.user, other_user )

        # send unfollow to foreign-author's inbox
        if other_user.type == 'foreign-author': 
            host = other_user.url.split('/')[2]
            if host == 'glowing-palm-tree1.herokuapp.com':
                token = TEAM_12_TOKEN
            elif host == 'cmput404-socialdistributio-t18.herokuapp.com':
                token = TEAM_18_TOKEN
            elif host == 'ourbackend.herokuapp.com':
                token = TEAM_02_TOKEN
            
            headers = {'Authorization': 'Token %s' % token}

            instance = {'from_user':request.user.id, 'to_user':other_user_id}
            serializer = ForeignFriendRequestSerializer(instance).unfollow()
            inboxURL = other_user.url + '/inbox/'
            requests.post(inboxURL, json=serializer, headers=headers)

        return redirect('app:view-other-user', other_user_id=other_user_id)

@login_required
def create_comment(request, post_id):
    """
    Displays a text form to allow the user to add a comment to the post given by post_id.
    """
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

@login_required
def create_foreign_comment(request):
    if request.method == 'POST':
        return redirect('app:foreign_posts')
    else: 
        post = request.session['foreign_post']
        url = post['author']['host']
        node = Node.objects.get(url__contains=url)
        node_interface = Node_Interface_Factory.get_interface(node)

    context = {
        'post': post,
        'is_author': False,
        'user' : request.user,
        'token' : node.auth_token
    }

    return render(request, 'comments/create_foreign_comment.html', context)

@login_required
def view_foreign_comment(request):
    if request.method == 'POST':
        return redirect('app:foreign_posts')
    else: 
        post = request.session['foreign_post']
        url = post['author']['host']
        node = Node.objects.get(url__contains=url)
        node_interface = Node_Interface_Factory.get_interface(node)
        comments = node_interface.get_comments(node, post_url=post['id'])

    context = {
        'post': post,
        'comments': comments,
        'is_author': False,
        'user' : request.user,
        'token' : node.auth_token
    }

    return render(request, 'comments/foreign_comments.html', context)


def comments(request, post_id):
    """
    Displays all of the comments for the post given by post_id.

    If the request has button, it also adds a like to that comment.
    """
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
    """
    View that adds a like to the post given by post_id.
    """
    user = request.user
    post = get_object_or_404(Post, pk=post_id)

    like = Like.objects.create_like(
        author=user,
        content_object=post
    )

@login_required
def like_comment(request, comment_id):
    """
    A view that adds a like to the comment given by comment_id.

    Typically triggered by a GET request to `comments` view.
    """
    user = request.user
    comment = get_object_or_404(Comment, pk=comment_id)

    like = Like.objects.create_like(
        author=user,
        content_object=comment
    )

@login_required
def inbox(request, author_id):
    """
    A view to manage and display the inbox for the author given by author_id.

    If the request is GET, it renders the paginated list of inbox items by sending a
    request to the inbox API endpoint.

    If the request is DELETE, it clears the author's inbox by sending a delete request
    to the inbox API endpoint
    """
    url = HOST_URL+reverse('api:inbox', kwargs={'author_id': author_id})
    token, _ = Token.objects.get_or_create(user=request.user) # create token
    headers = {'Authorization': 'Token %s' % token}
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

        req = requests.get(url, headers=headers)
        Token.objects.get(user=request.user).delete() # clean token
        res = json.loads(req.content.decode('utf-8'))
        res['author'] = request.path.split('/')[3]
        return render(request, 'app/inbox.html', {'res': res, 'token': API_TOKEN})
    elif request.method == "DELETE":
        req = requests.delete(url, headers=headers)
        Token.objects.get(user=request.user).delete() # clean token
        return HttpResponse(status=req.status_code)
    else:
        return HttpResponseNotAllowed


class PostListView(generic.ListView):
    """
    Renders a list of all th public posts (foreign and local) available to the user.
    """
    model = Post
    template_name = 'posts/public_posts.html'
    
    def get(self, request):
        queryset = Post.objects.filter(visibility="public", unlisted=False)[:20]
        serializer = PostSerializer(queryset, many=True)

        posts = []

        for node in Node.objects.get_queryset().filter(is_active=True):
            node_interface = Node_Interface_Factory.get_interface(node)
            authors = node_interface.get_authors(node)
            for author in authors:
                author_posts = node_interface.get_author_posts(node, author['id'])
                posts.extend(author_posts)

        for post in serializer.data:
            post_id = post['id'].split('/')[-1]
            url = f'{HOST_URL}/app/posts/{post_id}'
            post['id'] = post_id
            post['source'] = url
            post['origin'] = url
            post['local'] = True
            content = post['content'].strip(' ')
            post['content'] = content
            posts.append(post)

        return render(request, self.template_name, {'post_list': sorted(posts, key=lambda i: i['published'], reverse=True)})
      
@login_required
def sync_github_activity(request):
    """
    A view the pulls in the users github activity into their stream.

    Typically triggered from the `view_profile` view.
    """
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
    """
    a utility function to convert raw github API response into a post
    that our frontend can handle and display.
    """
    type = Post.ContentType.PLAIN
    title = f"Github: {event['type']}"
    categories = f"github, {event['type']}"
    try:
        head = str(event['payload']['head'])
    except KeyError:
        head = "N/A"
    try:
        messages = []
        for commit in event['payload']['commits']:
            messages.append(commit['message'])
        messages = ", ".join(messages)
    except KeyError:
        messages = "N/A"
    text_content = f"""
    Repository: {str(event['repo']['name'])}\n
    URL: https://github.com/{str(event['repo']['name'])}\n
    Payload:\n
    \t head: {head}\n
    \t messages when commiting: \n
    \t\t\t\t{messages}\n
    """


    post = Post.objects.create_post(
        author=author, 
        categories=categories,
        image_content=None,
        text_content=text_content,
        title=title,
        visibility=Post.Visibility.PUBLIC,
        unlisted=False,
        )
            