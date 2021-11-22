import os
import json

from drf_yasg import openapi

from django.db.models import aggregates, query
from dotenv import load_dotenv
import rest_framework.status as status
from django.shortcuts import get_object_or_404
from dotenv import load_dotenv
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.decorators import api_view
from django.http.response import HttpResponse
from rest_framework.views import APIView
from app.forms import PostCreationForm
from .models import User, Post
from .serializers import FollowersSerializer, PostSerializer, UserSerializer
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from friendship.models import Follow
from .models import Inbox as InboxItem
from .models import Post, User, Like, Comment
from .serializers import LikeSerializer, LikedSerializer, InboxSerializer, PostSerializer, UserSerializer, CommentSerializer

load_dotenv()
HOST_API_URL = os.getenv("HOST_API_URL")


class Author(APIView):
    """
    Endpoint for getting and updating author's on the server.
    """

    def get_author(self, author_id):
        return get_object_or_404(User, pk=author_id)

    @swagger_auto_schema(
        responses={
            200: openapi.Response(description="Author Found.", examples={"application/json": {
                "type": "author",
                "id": "http://127.0.0.1:8000/api/author/077d7a7e-304c-4f34-9d8f-d3c61e214b35",
                "host": "http://127.0.0.1:8000/api/",
                "displayName": "exampleAuthor",
                "url": "http://127.0.0.1:8000/api/077d7a7e-304c-4f34-9d8f-d3c61e214b35",
                "github": "http://github.com/exampleAuthor"
            }}),
            404: openapi.Response(description="Author Not Found.", examples={"application/json": {'detail': 'Not Found.'}}),
            400: openapi.Response(description="Method Not Allowed.", examples={"application/json": {'detail': "Method \"PUT\" not allowed."}})
        }
    )
    def get(self, request, author_id):
        """
        GETs and returns an Author object with id {author_id}, if one exists.

        GETs and returns an Author object with id {author_id}, if one exists.
        """
        author_model = self.get_author(author_id)
        serializer = UserSerializer(author_model)
        return Response(serializer.data)

    @swagger_auto_schema(
        responses={
            200: openapi.Response(description="Author Updated Succesfully.", examples={"application/json": {
                "type": "author",
                "id": "http://127.0.0.1:8000/api/author/077d7a7e-304c-4f34-9d8f-d3c61e214b35",
                "host": "http://127.0.0.1:8000/api/",
                "displayName": "exampleAuthor",
                "url": "http://127.0.0.1:8000/api/077d7a7e-304c-4f34-9d8f-d3c61e214b35",
                "github": "http://github.com/exampleAuthor"
            }}),
            404: openapi.Response(description="Author Not Found.", examples={"application/json": {'detail': 'Not Found.'}}),
            400: openapi.Response(description="Method Not Allowed.", examples={"application/json": {'detail': "Method \"PUT\" not allowed."}})
        },
        request_body=UserSerializer
    )
    def post(self, request, author_id):
        """
        Updates and returns the updated Author object with id {author_id}, if the Author exists.

        Not all fields need to be sent in the request body.
        """
        author_model = self.get_author(author_id)
        serializer = UserSerializer(author_model, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='get',
    responses={
        200: openapi.Response(description="Success",
                              examples={"application/json": [{
                                  "type": "author",
                                  "id": "http://127.0.0.1:8000/api/author/077d7a7e-304c-4f34-9d8f-d3c61e214b35",
                                  "host": "http://127.0.0.1:8000/api/",
                                  "displayName": "Bill",
                                  "url": "http://127.0.0.1:8000/api/077d7a7e-304c-4f34-9d8f-d3c61e214b35",
                                  "github": "http://github.com/bill123"
                              },
                                  {
                                  "type": "author",
                                  "id": "http://127.0.0.1:8000/api/author/077d7a7e-304c-4f34-9d8f-d3c61e214b35",
                                  "host": "http://127.0.0.1:8000/api/",
                                  "displayName": "Frank",
                                  "url": "http://127.0.0.1:8000/api/077d7a7e-304c-4f34-9d8f-d3c61e214b35",
                                  "github": "http://github.com/FrankFrank"
                              }
                              ]}),
        400: openapi.Response(description="Method Not Allowed.", examples={"application/json": {'detail': "Method \"POST\" not allowed."}})
    },
    paginator_inspectors='d',
    tags=['author'],
    manual_parameters=[
        openapi.Parameter(
            'page', openapi.IN_QUERY, description='A page number within the paginated result set.', type=openapi.TYPE_INTEGER),
        openapi.Parameter(
            'size', openapi.IN_QUERY, description='The size of the page to be returned', type=openapi.TYPE_INTEGER)
    ])
@ api_view(["GET"])
def authors(request):
    """
    GETs and returns a paginated list of all Authors on the server. 

    Pagination settings are passed as url parameters: ~/inbox/?page=1&size=5
    """
    paginator = PageNumberPaginationWithCount()
    query_params = request.query_params
    query_set = User.objects.all().filter(type="author")

    if query_params:
        size = query_params.get("size")
        if size:
            paginator.page_size = size
        authors = paginator.paginate_queryset(query_set, request)
    else:
        authors = query_set

    serializer = UserSerializer(authors, many=True)
    data = {"type": "authors", "items": serializer.data}

    return Response(data, status=status.HTTP_200_OK)

class PostAPI(APIView):
    @swagger_auto_schema(tags=['posts'])
    def get(self, request, *args, **kwargs):
        """
        GETs and returns a serialized post object which matches with the post_id provided
        
        GETs and returns a serialized post object which matches with the post_id provided
        """
        post_id = kwargs.get('post_id')
        post = get_object_or_404(Post, pk=post_id)
        serializer = PostSerializer(post)
        return JsonResponse(serializer.data)
    
    @swagger_auto_schema(tags=['posts'])
    def put(self, request, *args, **kwargs):
        """
        PUTs a post creating an entry on the server at
        the specified post id
        
        PUTs a post creating an entry on the server at
        the specified post id
        """
        post_id = kwargs.get('post_id')
        request.data['id'] = post_id
        serializer = PostSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return HttpResponse("Sucessfully created post\n")

        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(tags=['posts'])
    def post(self, request, *args, **kwargs):
        """
        Updates a post on the server which matches the given post id
        
        Updates a post on the server which matches the given post id
        """
        post_id = kwargs.get('post_id')

        query_set = Post.objects.filter(id=post_id)
        data = request.data

        posts_updated = query_set.update(**data)

        if posts_updated == 0:
            return HttpResponse("Something went wrong!")
        

        return HttpResponse("Successfully edited post")
    
    @swagger_auto_schema(tags=['posts'])
    def delete(self, request, *args, **kwargs):
        """
        DELETEs a post on the server which matches the given post id
        
        DELETEs a post on the server which matches the given post id
        """
        post_id = kwargs.get('post_id')
        post = get_object_or_404(Post, pk=post_id)
        post.delete()
        return HttpResponse("Successfully deleted")

class PageNumberPaginationWithCount(PageNumberPagination):
    # Q: https://stackoverflow.com/q/40985248 (Stupid.Fat.Cat)
    # A: https://stackoverflow.com/a/54843913 (Rashid Mahmood)
    # CC BY-SA 4.0
    def get_paginated_response(self, data):
        response = super(PageNumberPaginationWithCount,
                         self).get_paginated_response(data)
        response.data['total_pages'] = list(
            range(1, self.page.paginator.num_pages+1))
        if response.data['next']:
            response.data['next'] = response.data['next'].replace('api', 'app')
        if response.data['previous']:
            response.data['previous'] = response.data['previous'].replace(
                'api', 'app')
            if 'page' not in response.data['previous']:
                response.data['previous'] = response.data['previous'].replace(
                    '?', '?page=1&')  # need to correct route for front end pagination to work
        return response

class Like_Post_API(APIView):
    @swagger_auto_schema(tags=['likes'])
    def get(self, request, *args, **kwargs):
        """
        GETs and returns a list of likes on a post within the server which matches the given post id
        
        GETs and returns a list of likes on a post within the server which matches the given post id
        """
        post_id = self.kwargs.get('post_id')
        query_set = Like.objects.filter(object_id=post_id)

        serializer = LikeSerializer(query_set, many=True)
        data = serializer.data

        return Response(data, status.HTTP_200_OK)

class Like_Comment_API(APIView):
    @swagger_auto_schema(tags=['likes'])
    def get(self, request, *args, **kwargs):
        """
        GETs and returns a list of likes on a comment within the server which matches the given comment id
        
        GETs and returns a list of likes on a comment within the server which matches the given comment id
        """
        comment_id = self.kwargs.get('comment_id')
        query_set = Like.objects.filter(object_id=comment_id)

        serializer = LikeSerializer(query_set, many=True)
        data = serializer.data

        return Response(data, status.HTTP_200_OK)

class Liked_API(APIView):
    @swagger_auto_schema(tags=['likes'])
    def get(self, request, *args, **kwargs):
        """
        GETs and returns a list of every like object corresponding to a user on the server who matches the given author id
        
        GETs and returns a list of every like object corresponding to a user on the server who matches the given author id
        """
        author_id = self.kwargs.get('author_id')
        query_set = Like.objects.filter(author_id=author_id)

        serializer = LikedSerializer(query_set, many=True)
        data = serializer.data

        return Response(data, status.HTTP_200_OK)

class Comment_API(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    @swagger_auto_schema(tags=['comments'])
    def get(self, request, *args, **kwargs):
        """
        GETs and returns a paginated list of comments which correspond to the post which matches the given post id
        
        GETs and returns a paginated list of comments which correspond to the post which matches the given post id
        """
        paginator = PageNumberPaginationWithCount()
        author_id = self.kwargs.get('author_id')
        post_id = self.kwargs.get('post_id')

        query_set = Comment.objects.filter(post_id=post_id)

        size = request.query_params.get('size', 10)
        page = request.query_params.get('page', 1)
        paginator.page_size = size
        paginator.page = page
        
        paginated_qs = paginator.paginate_queryset(query_set, request)

        items = []
        for item in paginated_qs:
            serializer = CommentSerializer(item)
            items.append(serializer.data)
        
        paginated_response = paginator.get_paginated_response(paginated_qs)
        data = {
            'type': 'comment',
            'prev': paginated_response.data.get('previous'), 'size': size,
            'page': paginator.get_page_number(request, paginated_qs),
            'total_pages': paginated_response.data.get('total_pages'),
            'items': items
        }

        return Response(data, status=status.HTTP_200_OK)

    @swagger_auto_schema(tags=['comments'])
    def post(self, request, *args, **kwargs):
        """
        Creates a comment on a post which is on the server and whose id matches the given post id. Authors the comment with the given author id
        
        Creates a comment on a post which is on the server and whose id matches the given post id. Authors the comment with the given author id
        """
        author_id = self.kwargs.get('author_id')
        post_id = self.kwargs.get('post_id')

        request.data['post'] = post_id
        request.data['author'] = author_id

        serializer = CommentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            post = get_object_or_404(Post, pk=post_id)
            post.count += 1
            post.save()
            return Response(status.HTTP_204_NO_CONTENT)

        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Inbox(generics.ListCreateAPIView, generics.DestroyAPIView):
    serializer_class = InboxSerializer

    @swagger_auto_schema(
        responses={200: openapi.Response(description='Successfully get inbox items.',
                                         examples={"application/json":
                                                   {
                                                       "type": "inbox",
                                                       "author": "http://127.0.0.1:8000/api/author/077d7a7e-304c-4f34-9d8f-d3c61e214b35",
                                                       "next": "http://127.0.0.1:8000/app/author/077d7a7e-304c-4f34-9d8f-d3c61e214b35/inbox/?page=2&size=5",
                                                       "prev": 'null',
                                                       "size": "5",
                                                       "page": "1",
                                                       "total_pages": [
                                                           1, 2
                                                       ],
                                                       "items": [
                                                           {
                                                               "type": "post",
                                                               "title": "Test",
                                                               "id": "5836ca64-16d5-4b69-872a-41ca3ec25bf9",
                                                               "source": "http://127.0.0.1:8000/api/posts/5836ca64-16d5-4b69-872a-41ca3ec25bf9",
                                                               "origin": "http://127.0.0.1:8000/api/posts/5836ca64-16d5-4b69-872a-41ca3ec25bf9",
                                                               "description": "Test: This is my post....",
                                                               "contentType": "text/plain",
                                                               "content": "This is my post.",
                                                               "author": "077d7a7e-304c-4f34-9d8f-d3c61e214b35",
                                                               "categories": [
                                                                   "New",
                                                                   " Post",
                                                                   " Test"
                                                               ],
                                                               "count": 0,
                                                               "size": 0,
                                                               "comment_page": "http://127.0.0.1:8000/api/posts/5836ca64-16d5-4b69-872a-41ca3ec25bf9/comments",
                                                               "published": "2021-10-20T14:06:58.121854-06:00",
                                                               "visibility": "public",
                                                               "unlisted": 'true'
                                                           }, '...'
                                                       ]
                                                   }
                                                   })},
        tags=['inbox'],
        manual_parameters=[
            openapi.Parameter(
                'size', openapi.IN_QUERY, description='The size of the page to be returned', type=openapi.TYPE_INTEGER)
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        Retrieve a paginated list of {authord_id}'s inbox.

        Pagination settings are passed as url parameters: ~/author/{author_id}/inbox/?page=1&size=5
        """
        paginator = PageNumberPaginationWithCount()
        author_id = self.kwargs.get('author_id')
        query_set = InboxItem.objects.filter(author_id=author_id)
        size = request.query_params.get('size', 10)
        page = request.query_params.get('page', 1)
        paginator.page = page
        paginator.page_size = size
        paginated_qs = paginator.paginate_queryset(query_set, request)

        items = InboxSerializer(paginated_qs, many=True).data
        p = paginator.get_paginated_response(paginated_qs)
        data = {
            'type': 'inbox', 
            'author': HOST_API_URL+'/author/'+author_id, 
            'items': items,
            'next': p.data.get('next'),
            'prev': p.data.get('previous'), 'size': size,
            'page': paginator.get_page_number(request, paginated_qs),
            'total_pages': p.data.get('total_pages'),}


        return Response(data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        responses={
            204: openapi.Response(description="Succesfully POST an item to an author's inbox."),
        },
        tags=['inbox'])
    def post(self, request, author_id, *args, **kwargs):
        """
        Send an item to {author_id}'s inbox. For now, posts are the only accepted objects.

        'post' is the only content_type that is supported at this time.
        """
        try:
            item = request.data
            author = User.objects.get(id=author_id)
            InboxItem.objects.create(author_id=author.id, item=item)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @ swagger_auto_schema(
        responses={
            204: openapi.Response(description="Inbox successfully deleted."),
        },
        tags=['inbox'])
    def delete(self, request, *args, **kwargs):
        """
        Delete all items in {author_id}'s Inbox.
        
        Delete all items in {author_id}'s Inbox.
        """
        try:
            author_id = self.kwargs.get('author_id')
            inbox = InboxItem.objects.filter(author_id=author_id)
            inbox.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(method='GET', tags=['followers'], responses={
    200: openapi.Response(description="Sucessfully GET {author_id}'s followers", examples=
    {'application/json':{
    "type": "followers",
    "items": [
        {
            "type": "author",
            "id": "http://127.0.0.1:8000/api/author/628fbb7e-d856-42b1-97c8-4276f1ebf18f",
            "host": "http://127.0.0.1:8000/api/",
            "displayName": "bob",
            "url": "http://127.0.0.1:8000/api/628fbb7e-d856-42b1-97c8-4276f1ebf18f",
            "github": "http://github.com/bob123"
        },
        {
            "type": "author",
            "id": "http://127.0.0.1:8000/api/author/533bb187-de22-41fe-86f7-11a037d7adfe",
            "host": "http://127.0.0.1:8000/api/",
            "displayName": "bill",
            "url": "http://127.0.0.1:8000/api/533bb187-de22-41fe-86f7-11a037d7adfe",
            "github": "http://github.com/billy"
        }]}}),
    400: openapi.Response(description="Bad Request")
    })
@api_view(['GET'])
def followers(request, author_id):
    """
    GETs a list of authors who are following {author_id}

    GETs a list of authors who are following {author_id}
    """
    try:
        queryset = Follow.objects.filter(followee_id=author_id)
        serializer = FollowersSerializer(queryset, many=True)
        data = {'type': 'followers', 'items': serializer.data}

        return Response(data, status=status.HTTP_200_OK)
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)

class Followers(APIView):
    @swagger_auto_schema(tags=['followers'],
    responses={
        200: openapi.Response(
            description="{foreign_author_id} is following {author_id}",
            examples=
                {'application/json': {
                "type": "followers",
                "is_following": "true"
                }}),
        400: openapi.Response(description="Bad Request")
    }
    )
    def get(self, request, *args, **kwargs):
        """
        Check if {foreign_author_id} is following {author_id}
        
        Returns is_following: true if {foreign_author_id} is following {author_id}, is_following: false if not.
        """
        try: 
            author_id = kwargs.get('author_id')
            foreign_author_id = kwargs.get('foreign_author_id')
            is_following = Follow.objects.filter(followee_id=author_id, follower_id=foreign_author_id)
            # Not sure what to return? This should do for now.
            if is_following.exists():
                data = {'type': 'followers', 'is_following': 'true'}
            else:
                data = {'type': 'followers', 'is_following': 'false'}
            return Response(data, status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    # TODO: must be authenticated
    @swagger_auto_schema(tags=['followers'],
        responses={
        204: openapi.Response(
            description="Follower added"),
        400: openapi.Response(description="Bad Request")}
    )
    def post(self, request, *args, **kwargs):
        """
        Add {foreign_author_id} as a follower of {author_id}
        
        Add {foreign_author_id} as a follower of {author_id}
        """
        try:
            author_id = kwargs.get('author_id')
            author = User.objects.get(id=author_id)
            foreign_author_id = kwargs.get('foreign_author_id')
            foreign_author = User.objects.get(id=foreign_author_id)
            Follow.objects.add_follower(author, foreign_author)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(tags=['followers'],
        responses={
        204: openapi.Response(
            description="Follower removed"),
        400: openapi.Response(description="Bad Request")}
    )
    def delete(self, request, *args, **kwargs):
        """
        Remove {foreign_author_id} from {author_id} followers
        
        Remove {foreign_author_id} from {author_id} followers
        """
        try:
            author_id = kwargs.get('author_id')
            author = User.objects.get(id=author_id)
            foreign_author_id = kwargs.get('foreign_author_id')
            foreign_author = User.objects.get(id=foreign_author_id)
            Follow.objects.remove_follower(author, foreign_author)  # unfollow 
            return Response(status=status.HTTP_204_NO_CONTENT)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)