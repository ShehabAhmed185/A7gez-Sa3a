from rest_framework import serializers
from .models import Club, ClubImage

class ClubImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)

    class Meta:
        model = ClubImage
        fields = ["id", "image"]

class ClubSerializer(serializers.ModelSerializer):
    images = ClubImageSerializer(many=True, read_only=True)

    class Meta:
        model = Club
        fields = [
            "id",
            "title",
            "code",
            "zone",
            "address",
            "num_of_fields",
            "images"
        ]