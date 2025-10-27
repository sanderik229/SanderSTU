from rest_framework import viewsets, permissions, filters
from .models import Blogger, AdOffer
from .serializers import BloggerSerializer, AdOfferSerializer


class BloggerViewSet(viewsets.ModelViewSet):
    queryset = Blogger.objects.all()
    serializer_class = BloggerSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "topic", "social_network"]
    ordering_fields = ["audience_size", "name"]


class AdOfferViewSet(viewsets.ModelViewSet):
    queryset = AdOffer.objects.all()
    serializer_class = AdOfferSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "description", "blogger__name", "blogger__topic", "blogger__social_network"]
    ordering_fields = ["price"]


