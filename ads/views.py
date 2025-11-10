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
    permission_classes = [permissions.IsAuthenticated]  # Require authentication for all orders

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_authenticated and not (self.request.user.is_staff or getattr(self.request.user.profile, "role", "user") == "admin"):
            qs = qs.filter(user=self.request.user)
        return qs

    def perform_create(self, serializer):
        # User must be authenticated to create orders
        if not self.request.user.is_authenticated:
            from rest_framework.exceptions import AuthenticationFailed
            raise AuthenticationFailed("Для создания заказа необходимо авторизоваться. Пожалуйста, войдите в систему или зарегистрируйтесь.")
        
        user = self.request.user
        offer_id = self.request.data.get('offer_id')
        
        # If offer_id is provided, get the offer
        offer = None
        if offer_id:
            try:
                from bloggers.models import AdOffer
                offer = AdOffer.objects.get(id=offer_id)
            except AdOffer.DoesNotExist:
                pass
        
        order = serializer.save(user=user, offer=offer, order_type='offer' if offer else 'personal')
        
        # Если это персональный заказ, создаем ManagerOrder для менеджера
        if order.order_type == 'personal':
            try:
                from managers.models import Manager, ManagerOrder
                # Получаем первого активного менеджера или создаем без менеджера
                manager = Manager.objects.filter(is_active=True).first()
                if manager:
                    # Создаем ManagerOrder на основе персонального заказа
                    manager_order = ManagerOrder.objects.create(
                        manager=manager,
                        order_type='personal',
                        status='new',
                        client_name=(order.full_name or user.get_full_name() or user.email or 'Клиент')[:200],
                        client_email=order.email or user.email or '',
                        client_phone=order.phone or '',
                        service_description=order.description or 'Описание не указано',
                        budget=order.budget or 0
                    )
                    print(f"✓ Created ManagerOrder #{manager_order.id} for Order #{order.id} (Manager: {manager.user.email})")
            except Exception as e:
                print(f"✗ Error creating ManagerOrder: {e}")
                import traceback
                traceback.print_exc()

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


