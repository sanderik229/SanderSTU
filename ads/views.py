from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
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

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def pay(self, request, pk=None):
        """Обработка платежа за заказ"""
        order = self.get_object()
        
        # Проверяем, что заказ принадлежит пользователю
        if order.user != request.user:
            return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
        
        # Проверяем, что заказ еще не оплачен
        if order.status == 'paid':
            return Response({'error': 'Order already paid'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Получаем данные платежа
        payment_data = request.data
        amount = payment_data.get('amount')
        payment_method = payment_data.get('payment_method', 'card')
        
        # Обновляем статус заказа
        order.status = 'paid'
        order.payment_status = 'paid'
        order.payment_amount = amount
        order.payment_date = timezone.now()
        order.save()
        
        return Response({
            'success': True,
            'message': 'Payment processed successfully',
            'order_id': order.id,
            'status': order.status
        })


