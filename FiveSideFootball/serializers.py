from rest_framework import serializers
from .models import Field


class FieldSerializer(serializers.ModelSerializer):
    club_name = serializers.CharField(source='club.title', read_only=True)

    class Meta:
        model = Field
        fields = [
            'id',
            'field_name',
            'code',
            'club',
            'club_name',
            'hour_rate',
        ]
        read_only_fields = ['id']