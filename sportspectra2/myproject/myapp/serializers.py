from rest_framework import serializers
from .models import AuthUser, Stream

class AuthUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthUser
        fields = '__all__'

class LivestreamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stream
        fields = '__all__'