from rest_framework import serializers
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["id", "user", "blogger", "offer", "rating", "text", "created_at"]
        read_only_fields = ["user", "created_at"]


