from rest_framework import serializers
from .models import Blogger, AdOffer


class BloggerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blogger
        fields = ["id", "name", "social_network", "topic", "audience_size"]


class AdOfferSerializer(serializers.ModelSerializer):
    blogger = BloggerSerializer(read_only=True)
    blogger_id = serializers.PrimaryKeyRelatedField(queryset=Blogger.objects.all(), source="blogger", write_only=True)

    class Meta:
        model = AdOffer
        fields = ["id", "blogger", "blogger_id", "title", "description", "price", "is_active"]


