from rest_framework import serializers


class AddSerializer(serializers.Serializer):
    unique_identifier = serializers.CharField(max_length=40)

    inside_request = serializers.BooleanField(default=False)
    source = serializers.CharField(max_length=50)
    group = serializers.CharField(max_length=50)


class RemoveSerializer(serializers.Serializer):
    unique_identifier = serializers.CharField(max_length=40) 

    access_code = serializers.CharField(max_length=50)
