import os
from re import I
from dotenv import load_dotenv
from .models import HOST_API_URL, Post, User, Like
from django.shortcuts import get_object_or_404
from .models import User, Inbox, Comment
from rest_framework import serializers
from django.db.models import fields


load_dotenv()
HOST_API_URL = os.getenv("HOST_API_URL")
GITHUB_URL = os.getenv("GITHUB_URL")


class UserSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        user = super().to_representation(instance)
        user['id'] = HOST_API_URL+'author/'+user['id']
        if user['github']:
            user['github'] = GITHUB_URL + user['github']
        return user

    class Meta:
        model = User
        fields = ['type', 'id', 'host', 'displayName', 'url', 'github']


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

        author_id = post['author']
        author = User.objects.get(id=author_id)
        author_serializer = UserSerializer(author)

        post['author'] = author_serializer.data
        return post


class InboxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inbox
        fields =  ['item']
    
    def to_representation(self, instance):
        inbox = super().to_representation(instance)
        return inbox['item']

class LikeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Like
        fields = [
            'id',
            'context',
            'summary',
            'type',
            'author',
            'content_object'
        ]
    
    def to_representation(self, instance):
        like = super().to_representation(instance)

        like['@context'] = like.pop('context')
        like['object'] = like.pop('content_object').id

        author_id = like['author']
        author = User.objects.get(id=author_id)
        author_serializer = UserSerializer(author)

        like['author'] = author_serializer.data

        return like

class LikedSerializer(LikeSerializer):

    def to_representation(self, instance):
        liked = super().to_representation(instance)

        liked['type'] = 'liked'

        return liked

class CommentSerializer(serializers.ModelSerializer):

    contentType = serializers.CharField(source='content_type')

    class Meta:
        model = Comment
        fields = [
            'type',
            'author',
            'post',
            'comment',
            'contentType',
            'published',
            'id'
        ]
    
    def to_representation(self, instance):
        comment = super().to_representation(instance)

        author_id = comment['author']
        author = User.objects.get(id=author_id)
        author_serializer = UserSerializer(author)

        comment['author'] = author_serializer.data
        return comment

        
