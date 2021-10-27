from .models import User, Post
from .serializers import PostSerializer, UserSerializer
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
import rest_framework.status as status


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
