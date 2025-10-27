from rest_framework import serializers
from .models import Category, Order


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            "id", "user", "offer", "order_type", "status", "performance", "created_at",
            "full_name", "email", "phone", "ad_type", "budget", "description",
            "deadline", "requirements"
        ]
        read_only_fields = ["user", "created_at"]


