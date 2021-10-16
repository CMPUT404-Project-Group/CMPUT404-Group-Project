
from rest_framework import routers, serializers, viewsets
from .models import Post, User
class UserSerializer(serializers.HyperlinkedModelSerializer):
    displayName = serializers.CharField(source='username')
    class Meta:
        model = User
        fields = ['type', 'id', 'host', 'displayName', 'url', 'github']
    
#TODO: Correct field author, content, categories, published, and add field comments as listField
class PostSerializer(serializers.Serializer):
    type = serializers.CharField()
    id = serializers.CharField()
    title = serializers.CharField()
    source = serializers.URLField()
    origin = serializers.URLField()
    description = serializers.CharField()
    contentType = serializers.CharField(source='content_type')
    content = serializers.CharField(source='text_content')
    author = serializers.CharField()
    categories = serializers.CharField()
    count = serializers.IntegerField()
    size = serializers.IntegerField()
    comments = serializers.CharField(source='comment_page')
    visibility = serializers.CharField()
    unlisted = serializers.BooleanField()

    class Meta:
        model = Post