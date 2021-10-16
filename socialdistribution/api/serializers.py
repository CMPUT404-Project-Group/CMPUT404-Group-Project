
from rest_framework import routers, serializers, viewsets
from .models import Post, User
class UserSerializer(serializers.HyperlinkedModelSerializer):
    displayName = serializers.CharField(source='username')
    class Meta:
        model = User
        fields = ['type', 'id', 'host', 'displayName', 'url', 'github']