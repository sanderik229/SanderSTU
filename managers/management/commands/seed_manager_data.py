from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import models
from managers.models import Manager, AdService, ManagerOrder, WeeklyReport, Notification
from bloggers.models import Blogger
from decimal import Decimal
from datetime import datetime, timedelta
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Заполнить базу данных тестовыми данными для менеджеров'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Очистить существующие данные')

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Очистка существующих данных...')
            AdService.objects.all().delete()
            ManagerOrder.objects.all().delete()
            WeeklyReport.objects.all().delete()
            Notification.objects.all().delete()

        # Создаем тестовых блоггеров если их нет
        self.create_bloggers()
        
        # Создаем тестовые услуги
        self.create_services()
        
        # Создаем тестовые заказы
        self.create_orders()
        
        # Создаем тестовые отчеты
        self.create_reports()
        
        # Создаем тестовые уведомления
        self.create_notifications()

        self.stdout.write(
            self.style.SUCCESS('Тестовые данные успешно созданы!')
        )

    def create_bloggers(self):
        """Создаем тестовых блоггеров"""
        bloggers_data = [
            {
                'name': 'Анна Петрова',
                'social_network': 'instagram',
                'topic': 'Мода и красота',
                'audience_size': 50000
            },
            {
                'name': 'Михаил Иванов',
                'social_network': 'tiktok',
                'topic': 'Юмор и развлечения',
                'audience_size': 75000
            },
            {
                'name': 'Елена Смирнова',
                'social_network': 'vk',
                'topic': 'Образование',
                'audience_size': 30000
            },
            {
                'name': 'Дмитрий Козлов',
                'social_network': 'youtube',
                'topic': 'Технологии',
                'audience_size': 100000
            }
        ]

        for blogger_data in bloggers_data:
            blogger, created = Blogger.objects.get_or_create(
                name=blogger_data['name'],
                defaults=blogger_data
            )
            if created:
                self.stdout.write(f'Создан блоггер: {blogger.name}')

    def create_services(self):
        """Создаем тестовые услуги"""
        if not hasattr(User.objects.first(), 'manager_profile'):
            self.stdout.write('Нет менеджеров для создания услуг')
            return

        manager = Manager.objects.first()
        bloggers = Blogger.objects.all()
        
        if not bloggers.exists():
            self.stdout.write('Нет блоггеров для создания услуг')
            return

        services_data = [
            {
                'name': 'Реклама в Instagram Stories',
                'social_network': 'instagram',
                'price': Decimal('15000.00'),
                'description': 'Размещение рекламы в историях Instagram на 24 часа'
            },
            {
                'name': 'Обзор продукта на YouTube',
                'social_network': 'youtube',
                'price': Decimal('25000.00'),
                'description': 'Детальный обзор продукта в видео на YouTube канале'
            },
            {
                'name': 'Реклама в TikTok',
                'social_network': 'tiktok',
                'price': Decimal('12000.00'),
                'description': 'Создание рекламного видео для TikTok'
            },
            {
                'name': 'Пост в Telegram канале',
                'social_network': 'telegram',
                'price': Decimal('8000.00'),
                'description': 'Размещение рекламного поста в Telegram канале'
            },
            {
                'name': 'Реклама в VK',
                'social_network': 'vk',
                'price': Decimal('10000.00'),
                'description': 'Реклама в группе ВКонтакте'
            }
        ]

        for service_data in services_data:
            blogger = random.choice(bloggers)
            service, created = AdService.objects.get_or_create(
                name=service_data['name'],
                manager=manager,
                defaults={
                    **service_data,
                    'blogger': blogger
                }
            )
            if created:
                self.stdout.write(f'Создана услуга: {service.name}')

    def create_orders(self):
        """Создаем тестовые заказы"""
        manager = Manager.objects.first()
        if not manager:
            return

        orders_data = [
            {
                'order_type': 'personal',
                'status': 'new',
                'client_name': 'Иван Петров',
                'client_email': 'ivan@client.com',
                'client_phone': '+7-999-555-55-55',
                'service_description': 'Нужна реклама нового приложения для фитнеса',
                'budget': Decimal('20000.00')
            },
            {
                'order_type': 'personal',
                'status': 'accepted',
                'client_name': 'Мария Сидорова',
                'client_email': 'maria@client.com',
                'client_phone': '+7-999-666-66-66',
                'service_description': 'Продвижение интернет-магазина одежды',
                'budget': Decimal('30000.00')
            },
            {
                'order_type': 'personal',
                'status': 'completed',
                'client_name': 'Алексей Новиков',
                'client_email': 'alexey@client.com',
                'client_phone': '+7-999-777-77-77',
                'service_description': 'Реклама курсов программирования',
                'budget': Decimal('15000.00')
            }
        ]

        for order_data in orders_data:
            order, created = ManagerOrder.objects.get_or_create(
                manager=manager,
                client_email=order_data['client_email'],
                defaults=order_data
            )
            if created:
                self.stdout.write(f'Создан заказ: {order.client_name}')

    def create_reports(self):
        """Создаем тестовые отчеты"""
        manager = Manager.objects.first()
        if not manager:
            return

        # Создаем отчеты за последние 4 недели
        today = datetime.now().date()
        for i in range(4):
            week_start = today - timedelta(days=today.weekday() + 7*i)
            week_end = week_start + timedelta(days=6)
            
            # Подсчитываем статистику
            orders_count = ManagerOrder.objects.filter(
                manager=manager,
                created_at__date__range=[week_start, week_end]
            ).count()
            
            total_revenue = ManagerOrder.objects.filter(
                manager=manager,
                created_at__date__range=[week_start, week_end]
            ).aggregate(total=models.Sum('budget'))['total'] or Decimal('0.00')
            
            active_services = AdService.objects.filter(
                manager=manager,
                is_active=True
            ).count()

            report, created = WeeklyReport.objects.get_or_create(
                manager=manager,
                week_start=week_start,
                week_end=week_end,
                defaults={
                    'total_orders': orders_count,
                    'total_revenue': total_revenue,
                    'active_services': active_services
                }
            )
            
            if created:
                self.stdout.write(f'Создан отчет за {week_start} - {week_end}')

    def create_notifications(self):
        """Создаем тестовые уведомления"""
        manager = Manager.objects.first()
        if not manager:
            return

        notifications_data = [
            {
                'notification_type': 'service_created',
                'title': 'Новая услуга создана',
                'message': 'Услуга "Реклама в Instagram Stories" была успешно создана'
            },
            {
                'notification_type': 'order_accepted',
                'title': 'Заказ принят',
                'message': 'Заказ #1 от Ивана Петрова был принят в работу'
            },
            {
                'notification_type': 'order_completed',
                'title': 'Заказ завершен',
                'message': 'Заказ #3 от Алексея Новикова был успешно завершен'
            },
            {
                'notification_type': 'report_generated',
                'title': 'Отчет сгенерирован',
                'message': 'Еженедельный отчет за текущую неделю был создан'
            }
        ]

        for notification_data in notifications_data:
            notification, created = Notification.objects.get_or_create(
                manager=manager,
                title=notification_data['title'],
                defaults=notification_data
            )
            if created:
                self.stdout.write(f'Создано уведомление: {notification.title}')
