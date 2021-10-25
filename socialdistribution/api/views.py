from rest_framework import generics
import rest_framework.status as status
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view
from rest_framework import serializers, status
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .serializers import PostSerializer, UserSerializer
from .serializers import UserSerializer, InboxSerializer
from .models import Inbox as InboxItem
from rest_framework.response import Response
from .models import User, Post
<< << << < HEAD
== == == =
>>>>>> > feat/post_serialization


# TODO: set up as protected endpoint
@api_view(["GET", "POST"])
def author(request, author_id):
    authorModel = get_object_or_404(User, pk=author_id)

    if request.method == "GET":
        serializer = UserSerializer(authorModel)
        return JsonResponse(serializer.data)

    elif request.method == "POST":
        serializer = UserSerializer(authorModel, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def authors(request):
    paginator = PageNumberPagination()
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

    return JsonResponse(data)


@api_view(["GET"])
def posts(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    serializer = PostSerializer(post)
    return JsonResponse(serializer.data)


class Inbox(generics.ListCreateAPIView, generics.DestroyAPIView):
    """
    Inbox class is responsible for managing the an author's (given by <str:author_id>) inbox.

    get_queryset() returns a paginated list of the author's inbox items.

    post(request, author_id) adds an object to the author's inbox.

    delete(request) deletes the author's inbox items.
    """
    serializer_class = InboxSerializer

    def get_queryset(self):
        author_id = self.kwargs.get('author_id')
        queryset = InboxItem.objects.filter(author_id=author_id)
        data = {"type": "inbox", "author": author_id, "items": []}
        # return JsonResponse(data)
        return queryset

    def post(self, request, author_id, *args, **kwargs):
        # TODO: probably want to get_object_or_404 here
        content_type = request.data["content_type"]
        object_id = request.data["object_id"]
        if content_type == "post":
            content_object = Post.objects.get(id=object_id)
            author = User.objects.get(id=author_id)
            inbox = InboxItem.objects.create(author_id=author,
                                             content_object=content_object)

            return Response({'type': inbox.content_object.author.displayName})

    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
