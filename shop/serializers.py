from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Category, Ad, Package, Order, Review


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug", "created_at", "updated_at"]


class AdSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source="category", write_only=True
    )

    class Meta:
        model = Ad
        fields = [
            "id",
            "title",
            "description",
            "category",
            "category_id",
            "price",
            "popularity",
            "image",
            "is_active",
            "created_at",
            "updated_at",
        ]


class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = ["id", "name", "description", "price", "is_active", "created_at", "updated_at"]


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            "id",
            "customer_name",
            "email",
            "phone",
            "description",
            "ad",
            "package",
            "status",
            "created_at",
            "updated_at",
        ]


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["id", "user_name", "rating", "text", "ad", "created_at", "updated_at"]


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=6)

    def create(self, validated_data):
        User = get_user_model()
        email = validated_data["email"].lower()
        user = User.objects.create_user(username=email, email=email, password=validated_data["password"])
        return user


