from rest_framework import viewsets, permissions, filters
from .models import Category, Order
from .serializers import CategorySerializer, OrderSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.AllowAny]  # Allow unauthenticated personal orders

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_authenticated and not (self.request.user.is_staff or getattr(self.request.user.profile, "role", "user") == "admin"):
            qs = qs.filter(user=self.request.user)
        return qs

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        offer_id = self.request.data.get('offer_id')
        
        # If offer_id is provided, get the offer
        offer = None
        if offer_id:
            try:
                from bloggers.models import AdOffer
                offer = AdOffer.objects.get(id=offer_id)
            except AdOffer.DoesNotExist:
                pass
        
        serializer.save(user=user, offer=offer, order_type='offer' if offer else 'personal')


