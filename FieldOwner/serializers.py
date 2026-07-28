from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import FieldOwner


class FieldOwnerSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = FieldOwner
        fields = '__all__'

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return FieldOwner.objects.create(**validated_data)