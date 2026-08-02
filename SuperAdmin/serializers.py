from rest_framework import serializers
from .models import SuperAdmin


class SuperAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuperAdmin
        fields = "__all__"
        extra_kwargs = {
            "password": {"write_only": True}
        }