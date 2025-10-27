from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Manager, AdService, ManagerOrder, WeeklyReport, Notification
from .serializers import (
    ManagerSerializer, AdServiceSerializer, ManagerOrderSerializer, 
    WeeklyReportSerializer, NotificationSerializer, BloggerSerializer
)
from bloggers.models import Blogger


class ManagerViewSet(viewsets.ModelViewSet):
    """ViewSet для управления менеджерами"""
    queryset = Manager.objects.all()
    serializer_class = ManagerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Менеджеры видят только свой профиль
        if hasattr(self.request.user, 'manager_profile'):
            return Manager.objects.filter(user=self.request.user)
        return Manager.objects.none()

    @action(detail=False, methods=['get'])
    def profile(self, request):
        """Получить профиль текущего менеджера"""
        if not hasattr(request.user, 'manager_profile'):
            return Response({'error': 'User is not a manager'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer(request.user.manager_profile)
        return Response(serializer.data)

    @action(detail=False, methods=['put'])
    def update_profile(self, request):
        """Обновить профиль менеджера"""
        if not hasattr(request.user, 'manager_profile'):
            return Response({'error': 'User is not a manager'}, status=status.HTTP_403_FORBIDDEN)
        
        manager = request.user.manager_profile
        serializer = self.get_serializer(manager, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdServiceViewSet(viewsets.ModelViewSet):
    """ViewSet для управления рекламными услугами"""
    queryset = AdService.objects.all()
    serializer_class = AdServiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Менеджеры видят только свои услуги
        if hasattr(self.request.user, 'manager_profile'):
            return AdService.objects.filter(manager=self.request.user.manager_profile)
        return AdService.objects.none()

    def perform_create(self, serializer):
        # Автоматически назначаем текущего менеджера
        if hasattr(self.request.user, 'manager_profile'):
            serializer.save(manager=self.request.user.manager_profile)

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Переключить статус активности услуги"""
        service = self.get_object()
        service.is_active = not service.is_active
        service.save()
        
        # Создаем уведомление
        notification_type = 'service_updated' if service.is_active else 'service_deleted'
        Notification.objects.create(
            manager=service.manager,
            notification_type=notification_type,
            title=f"Услуга {'активирована' if service.is_active else 'деактивирована'}",
            message=f"Услуга '{service.name}' была {'активирована' if service.is_active else 'деактивирована'}"
        )
        
        return Response({'is_active': service.is_active})

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Получить статистику по услугам"""
        if not hasattr(request.user, 'manager_profile'):
            return Response({'error': 'User is not a manager'}, status=status.HTTP_403_FORBIDDEN)
        
        manager = request.user.manager_profile
        services = AdService.objects.filter(manager=manager)
        
        stats = {
            'total_services': services.count(),
            'active_services': services.filter(is_active=True).count(),
            'total_revenue': services.aggregate(total=Sum('price'))['total'] or 0,
            'by_social_network': services.values('social_network').annotate(count=Count('id')),
            'by_blogger': services.values('blogger__name').annotate(count=Count('id'))
        }
        
        return Response(stats)


class ManagerOrderViewSet(viewsets.ModelViewSet):
    """ViewSet для управления заказами менеджера"""
    queryset = ManagerOrder.objects.all()
    serializer_class = ManagerOrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Менеджеры видят только свои заказы
        if hasattr(self.request.user, 'manager_profile'):
            return ManagerOrder.objects.filter(manager=self.request.user.manager_profile)
        return ManagerOrder.objects.none()

    def perform_create(self, serializer):
        # Автоматически назначаем текущего менеджера
        if hasattr(self.request.user, 'manager_profile'):
            serializer.save(manager=self.request.user.manager_profile)

    @action(detail=True, methods=['post'])
    def accept_order(self, request, pk=None):
        """Принять заказ"""
        order = self.get_object()
        if order.status != 'new':
            return Response({'error': 'Order is not in new status'}, status=status.HTTP_400_BAD_REQUEST)
        
        order.status = 'accepted'
        order.save()
        
        # Создаем уведомление
        Notification.objects.create(
            manager=order.manager,
            notification_type='order_accepted',
            title='Заказ принят',
            message=f'Заказ #{order.id} был принят в работу'
        )
        
        return Response({'status': order.status})

    @action(detail=True, methods=['post'])
    def complete_order(self, request, pk=None):
        """Завершить заказ"""
        order = self.get_object()
        if order.status not in ['accepted', 'in_progress']:
            return Response({'error': 'Order cannot be completed'}, status=status.HTTP_400_BAD_REQUEST)
        
        order.status = 'completed'
        order.save()
        
        # Создаем уведомление
        Notification.objects.create(
            manager=order.manager,
            notification_type='order_completed',
            title='Заказ завершен',
            message=f'Заказ #{order.id} был успешно завершен'
        )
        
        return Response({'status': order.status})

    @action(detail=False, methods=['get'])
    def personal_orders(self, request):
        """Получить персональные заказы менеджера"""
        if not hasattr(request.user, 'manager_profile'):
            return Response({'error': 'User is not a manager'}, status=status.HTTP_403_FORBIDDEN)
        
        manager = request.user.manager_profile
        personal_orders = ManagerOrder.objects.filter(
            manager=manager, 
            order_type='personal'
        ).order_by('-created_at')
        
        serializer = self.get_serializer(personal_orders, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def blogger_orders(self, request):
        """Получить заказы от блоггеров менеджера"""
        if not hasattr(request.user, 'manager_profile'):
            return Response({'error': 'User is not a manager'}, status=status.HTTP_403_FORBIDDEN)
        
        manager = request.user.manager_profile
        blogger_orders = ManagerOrder.objects.filter(
            manager=manager, 
            order_type='blogger'
        ).order_by('-created_at')
        
        serializer = self.get_serializer(blogger_orders, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def new_orders(self, request):
        """Получить новые заказы (персональные и от блоггеров)"""
        if not hasattr(request.user, 'manager_profile'):
            return Response({'error': 'User is not a manager'}, status=status.HTTP_403_FORBIDDEN)
        
        manager = request.user.manager_profile
        new_orders = ManagerOrder.objects.filter(
            manager=manager, 
            status='new'
        ).order_by('-created_at')
        
        serializer = self.get_serializer(new_orders, many=True)
        return Response(serializer.data)


class WeeklyReportViewSet(viewsets.ModelViewSet):
    """ViewSet для еженедельных отчетов"""
    queryset = WeeklyReport.objects.all()
    serializer_class = WeeklyReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Менеджеры видят только свои отчеты
        if hasattr(self.request.user, 'manager_profile'):
            return WeeklyReport.objects.filter(manager=self.request.user.manager_profile)
        return WeeklyReport.objects.none()

    @action(detail=False, methods=['post'])
    def generate_report(self, request):
        """Сгенерировать еженедельный отчет"""
        if not hasattr(request.user, 'manager_profile'):
            return Response({'error': 'User is not a manager'}, status=status.HTTP_403_FORBIDDEN)
        
        manager = request.user.manager_profile
        
        # Получаем даты недели
        week_start = request.data.get('week_start')
        week_end = request.data.get('week_end')
        
        if not week_start or not week_end:
            return Response({'error': 'week_start and week_end are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Проверяем, не существует ли уже отчет за эту неделю
        existing_report = WeeklyReport.objects.filter(
            manager=manager,
            week_start=week_start,
            week_end=week_end
        ).first()
        
        if existing_report:
            return Response({'error': 'Report for this week already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Собираем статистику
        orders = ManagerOrder.objects.filter(
            manager=manager,
            created_at__date__range=[week_start, week_end]
        )
        
        total_orders = orders.count()
        total_revenue = orders.aggregate(total=Sum('budget'))['total'] or 0
        active_services = AdService.objects.filter(manager=manager, is_active=True).count()
        
        # Создаем отчет
        report = WeeklyReport.objects.create(
            manager=manager,
            week_start=week_start,
            week_end=week_end,
            total_orders=total_orders,
            total_revenue=total_revenue,
            active_services=active_services
        )
        
        # Создаем уведомление
        Notification.objects.create(
            manager=manager,
            notification_type='report_generated',
            title='Отчет сгенерирован',
            message=f'Еженедельный отчет за {week_start} - {week_end} был создан'
        )
        
        serializer = self.get_serializer(report)
        return Response(serializer.data)


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для уведомлений"""
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Менеджеры видят только свои уведомления
        if hasattr(self.request.user, 'manager_profile'):
            return Notification.objects.filter(manager=self.request.user.manager_profile)
        return Notification.objects.none()

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Отметить уведомление как прочитанное"""
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'is_read': True})

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Отметить все уведомления как прочитанные"""
        if not hasattr(request.user, 'manager_profile'):
            return Response({'error': 'User is not a manager'}, status=status.HTTP_403_FORBIDDEN)
        
        manager = request.user.manager_profile
        Notification.objects.filter(manager=manager, is_read=False).update(is_read=True)
        return Response({'message': 'All notifications marked as read'})

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Получить количество непрочитанных уведомлений"""
        if not hasattr(request.user, 'manager_profile'):
            return Response({'error': 'User is not a manager'}, status=status.HTTP_403_FORBIDDEN)
        
        manager = request.user.manager_profile
        count = Notification.objects.filter(manager=manager, is_read=False).count()
        return Response({'unread_count': count})
