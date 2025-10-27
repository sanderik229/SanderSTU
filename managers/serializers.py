from rest_framework import serializers
from .models import Manager, AdService, ManagerOrder, WeeklyReport, Notification
from bloggers.models import Blogger


class ManagerSerializer(serializers.ModelSerializer):
    """Сериализатор для менеджера"""
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    active_orders_count = serializers.ReadOnlyField()
    managed_bloggers_count = serializers.ReadOnlyField()

    class Meta:
        model = Manager
        fields = [
            'id', 'user_email', 'user_full_name', 'phone', 'department', 
            'hire_date', 'is_active', 'active_orders_count', 'managed_bloggers_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AdServiceSerializer(serializers.ModelSerializer):
    """Сериализатор для рекламных услуг"""
    blogger_name = serializers.CharField(source='blogger.name', read_only=True)
    manager_name = serializers.CharField(source='manager.user.get_full_name', read_only=True)
    social_network_display = serializers.CharField(source='get_social_network_display', read_only=True)

    class Meta:
        model = AdService
        fields = [
            'id', 'name', 'social_network', 'social_network_display', 'price', 
            'description', 'blogger', 'blogger_name', 'manager', 'manager_name',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        # Автоматически назначаем текущего пользователя как менеджера
        request = self.context.get('request')
        if request and hasattr(request.user, 'manager_profile'):
            validated_data['manager'] = request.user.manager_profile
        return super().create(validated_data)


class ManagerOrderSerializer(serializers.ModelSerializer):
    """Сериализатор для заказов менеджера"""
    manager_name = serializers.CharField(source='manager.user.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    order_type_display = serializers.CharField(source='get_order_type_display', read_only=True)

    class Meta:
        model = ManagerOrder
        fields = [
            'id', 'manager', 'manager_name', 'order_type', 'order_type_display',
            'status', 'status_display', 'blogger_order', 'client_name', 
            'client_email', 'client_phone', 'service_description', 'budget',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        # Автоматически назначаем текущего пользователя как менеджера
        request = self.context.get('request')
        if request and hasattr(request.user, 'manager_profile'):
            validated_data['manager'] = request.user.manager_profile
        return super().create(validated_data)


class WeeklyReportSerializer(serializers.ModelSerializer):
    """Сериализатор для еженедельных отчетов"""
    manager_name = serializers.CharField(source='manager.user.get_full_name', read_only=True)
    pdf_url = serializers.SerializerMethodField()

    class Meta:
        model = WeeklyReport
        fields = [
            'id', 'manager', 'manager_name', 'week_start', 'week_end',
            'total_orders', 'total_revenue', 'active_services', 'pdf_file', 'pdf_url',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def get_pdf_url(self, obj):
        if obj.pdf_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.pdf_file.url)
        return None


class NotificationSerializer(serializers.ModelSerializer):
    """Сериализатор для уведомлений"""
    manager_name = serializers.CharField(source='manager.user.get_full_name', read_only=True)
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id', 'manager', 'manager_name', 'notification_type', 'notification_type_display',
            'title', 'message', 'is_read', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class BloggerSerializer(serializers.ModelSerializer):
    """Простой сериализатор для блоггеров"""
    class Meta:
        model = Blogger
        fields = ['id', 'name', 'social_network', 'topic', 'audience_size']
