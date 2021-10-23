from django.db.models import fields
from rest_framework import serializers
from .models import User, Inbox
from dotenv import load_dotenv
import os

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
