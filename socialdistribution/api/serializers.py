import os
from dotenv import load_dotenv
from .models import HOST_API_URL, Post, User
from django.shortcuts import get_object_or_404
from .models import User, Inbox
from rest_framework import serializers
from django.db.models import fields


load_dotenv()
HOST_API_URL = os.getenv("HOST_API_URL")
GITHUB_URL = os.getenv("GITHUB_URL")


class UserSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        user = super().to_representation(instance)
        user['id'] = HOST_API_URL+'author/'+user['id']
        user['github'] = GITHUB_URL + user['github']
        return user

    class Meta:
        model = User
        fields = ['type', 'id', 'host', 'displayName', 'url', 'github']


class InboxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inbox
        fields = ['author_id', 'content_object']


# TODO: images, author, comments, comments,
class PostSerializer(serializers.ModelSerializer):

    contentType = serializers.CharField(source='content_type')
    content = serializers.CharField(source='text_content')

    class Meta:
        model = Post
        fields = [
            'type',
            'title',
            'id',
            'source',
            'origin',
            'description',
            'contentType',
            'content',
            'author',
            'categories',
            'count',
            'size',
            'comment_page',
            'published',
            'visibility',
            'unlisted'
        ]

    def to_representation(self, instance):
        post = super().to_representation(instance)
        post['categories'] = post['categories'].split(',')
        return post
