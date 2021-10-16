
from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    displayName = serializers.CharField(source='username')

    def update(self, instance, validated_date):
        # print(instance, validated_data)
        # instance.username = validated_date.get(
        #     'displayName', instance.username)
        print(instance.id)
        super(UserSerializer, self.update(instance, validated_date))
        return instance

    class Meta:
        model = User
        fields = ['type', 'id', 'host', 'displayName', 'url', 'github']
