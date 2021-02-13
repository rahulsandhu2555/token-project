from rest_framework import serializers
from token_app.models import Tokens


class TokenSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    token = serializers.CharField(max_length=50)
    user = serializers.IntegerField(allow_null=True, required=False)
    time = serializers.DateTimeField()

    def create(self, validated_data):
        return Tokens.objects.create(**validated_data)

    def update(self, instance, validated_data):
        if 'user' in validated_data:
            instance.user = validated_data.get('user')