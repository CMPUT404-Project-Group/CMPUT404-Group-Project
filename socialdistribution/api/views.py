from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from .models import User, Post
from .serializers import PostSerializer, UserSerializer
from urllib import parse

@api_view(["GET"])
def author(request, author_id):
    author_id = parse.unquote(author_id.replace('_','%'))
    authorModel = get_object_or_404(User, pk=author_id)
    serializer = UserSerializer(authorModel)

    return JsonResponse(serializer.data)

@api_view(["GET"])
def post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    print(post)
    serializer = PostSerializer(post)

    return JsonResponse(serializer.data)

