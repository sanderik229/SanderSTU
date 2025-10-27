from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Manager(models.Model):
    """Модель менеджера с расширенной информацией"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='manager_profile')
    phone = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=100, blank=True)
    hire_date = models.DateField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Менеджер"
        verbose_name_plural = "Менеджеры"

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.user.email})"

    @property
    def active_orders_count(self):
        """Количество активных заказов менеджера"""
        return self.managed_orders.filter(status__in=['new', 'in_progress']).count()

    @property
    def managed_bloggers_count(self):
        """Количество блоггеров под управлением"""
        return self.managed_bloggers.count()


class AdService(models.Model):
    """Модель рекламной услуги"""
    SOCIAL_NETWORKS = [
        ('instagram', 'Instagram'),
        ('youtube', 'YouTube'),
        ('tiktok', 'TikTok'),
        ('telegram', 'Telegram'),
        ('vk', 'VKontakte'),
        ('facebook', 'Facebook'),
        ('twitter', 'Twitter'),
    ]

    name = models.CharField(max_length=200, verbose_name="Название услуги")
    social_network = models.CharField(max_length=20, choices=SOCIAL_NETWORKS, verbose_name="Социальная сеть")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    description = models.TextField(verbose_name="Описание")
    blogger = models.ForeignKey('bloggers.Blogger', on_delete=models.CASCADE, related_name='services', verbose_name="Блоггер")
    manager = models.ForeignKey(Manager, on_delete=models.CASCADE, related_name='services', verbose_name="Менеджер")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Рекламная услуга"
        verbose_name_plural = "Рекламные услуги"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.get_social_network_display()} ({self.blogger.name})"


class ManagerOrder(models.Model):
    """Модель заказа под управлением менеджера"""
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('accepted', 'Принят'),
        ('in_progress', 'В работе'),
        ('completed', 'Завершен'),
        ('cancelled', 'Отменен'),
    ]

    ORDER_TYPE_CHOICES = [
        ('blogger', 'От блоггера'),
        ('personal', 'Персональный'),
    ]

    manager = models.ForeignKey(Manager, on_delete=models.CASCADE, related_name='managed_orders')
    order_type = models.CharField(max_length=20, choices=ORDER_TYPE_CHOICES, default='blogger')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    
    # Связь с существующими заказами
    blogger_order = models.ForeignKey('ads.Order', on_delete=models.CASCADE, null=True, blank=True, related_name='manager_orders')
    
    # Персональные заказы
    client_name = models.CharField(max_length=200, blank=True)
    client_email = models.EmailField(blank=True)
    client_phone = models.CharField(max_length=20, blank=True)
    service_description = models.TextField(blank=True)
    budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Заказ менеджера"
        verbose_name_plural = "Заказы менеджеров"
        ordering = ['-created_at']

    def __str__(self):
        if self.order_type == 'blogger' and self.blogger_order:
            return f"Заказ #{self.blogger_order.id} от {self.blogger_order.user.get_full_name()}"
        return f"Персональный заказ от {self.client_name}"


class WeeklyReport(models.Model):
    """Модель еженедельного отчета"""
    manager = models.ForeignKey(Manager, on_delete=models.CASCADE, related_name='weekly_reports')
    week_start = models.DateField()
    week_end = models.DateField()
    total_orders = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    active_services = models.IntegerField(default=0)
    pdf_file = models.FileField(upload_to='reports/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Еженедельный отчет"
        verbose_name_plural = "Еженедельные отчеты"
        ordering = ['-week_start']

    def __str__(self):
        return f"Отчет {self.manager.user.get_full_name()} за {self.week_start} - {self.week_end}"


class Notification(models.Model):
    """Модель уведомлений"""
    NOTIFICATION_TYPES = [
        ('service_created', 'Создана услуга'),
        ('service_updated', 'Обновлена услуга'),
        ('service_deleted', 'Удалена услуга'),
        ('order_accepted', 'Заказ принят'),
        ('order_completed', 'Заказ завершен'),
        ('report_generated', 'Отчет сгенерирован'),
    ]

    manager = models.ForeignKey(Manager, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Уведомление"
        verbose_name_plural = "Уведомления"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.manager.user.get_full_name()}"
