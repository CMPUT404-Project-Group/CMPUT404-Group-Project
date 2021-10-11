from django.http import JsonResponse
from django.shortcuts import get_object_or_404, get_list_or_404
from rest_framework import serializers
from rest_framework.decorators import api_view
from .models import User
from .serializers import UserSerializer
from urllib import parse

# TODO: set up as protected endpoint


@api_view(["GET", "POST"])
def author(request, author_id):
    author_id = parse.unquote(author_id.replace('_', '%'))

    if request.method == "GET":
        authorModel = get_object_or_404(User, pk=author_id)
        serializer = UserSerializer(authorModel)
        return JsonResponse(serializer.data)

    elif request.method == "POST":
        pass

# TODO: set up as protected endpoint


@api_view(["GET"])
def authors(request):
    authors = User.objects.all().filter(type="author")
    serializer = UserSerializer(authors, many=True)

    data = {"type": "authors", "items": serializer.data}

    return JsonResponse(data)
