from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from managers.models import Manager, AdService, ManagerOrder, WeeklyReport, Notification
from bloggers.models import Blogger, AdOffer
from decimal import Decimal
from datetime import datetime, timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Создает тестовые данные для панели менеджера'

    def handle(self, *args, **options):
        # Создаем тестового блоггера
        blogger, created = Blogger.objects.get_or_create(
            name="Тестовый Блоггер",
            defaults={
                'social_network': 'instagram',
                'topic': 'Lifestyle',
                'audience_size': 50000
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Создан тестовый блоггер: {blogger.name}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Блоггер уже существует: {blogger.name}')
            )

        # Создаем тестовое предложение
        offer, created = AdOffer.objects.get_or_create(
            title="Тестовое предложение",
            defaults={
                'blogger': blogger,
                'social_network': 'instagram',
                'price': Decimal('15000.00'),
                'description': 'Тестовое предложение для проверки функционала'
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Создано тестовое предложение: {offer.title}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Предложение уже существует: {offer.title}')
            )

        # Получаем менеджера (если есть)
        try:
            manager = Manager.objects.first()
            if manager:
                # Создаем тестовую услугу
                service, created = AdService.objects.get_or_create(
                    name="Тестовая услуга Instagram",
                    defaults={
                        'manager': manager,
                        'social_network': 'instagram',
                        'price': Decimal('20000.00'),
                        'description': 'Тестовая услуга для проверки CRUD функционала',
                        'blogger': blogger,
                        'is_active': True
                    }
                )
                
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f'Создана тестовая услуга: {service.name}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'Услуга уже существует: {service.name}')
                    )

                # Создаем тестовый заказ
                order, created = ManagerOrder.objects.get_or_create(
                    client_name="Тестовый Клиент",
                    defaults={
                        'manager': manager,
                        'order_type': 'personal',
                        'status': 'new',
                        'client_email': 'test@example.com',
                        'client_phone': '+7 (999) 123-45-67',
                        'service_description': 'Тестовый заказ для проверки функционала',
                        'budget': Decimal('25000.00')
                    }
                )
                
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f'Создан тестовый заказ: #{order.id}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'Заказ уже существует: #{order.id}')
                    )

                # Создаем тестовый отчет
                week_start = datetime.now().date() - timedelta(days=7)
                week_end = datetime.now().date()
                
                report, created = WeeklyReport.objects.get_or_create(
                    manager=manager,
                    week_start=week_start,
                    week_end=week_end,
                    defaults={
                        'total_orders': 5,
                        'total_revenue': Decimal('125000.00'),
                        'active_services': 3
                    }
                )
                
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f'Создан тестовый отчет: {report.week_start} - {report.week_end}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'Отчет уже существует: {report.week_start} - {report.week_end}')
                    )

                # Создаем тестовое уведомление
                notification, created = Notification.objects.get_or_create(
                    title="Тестовое уведомление",
                    defaults={
                        'manager': manager,
                        'message': 'Это тестовое уведомление для проверки функционала',
                        'is_read': False
                    }
                )
                
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f'Создано тестовое уведомление: {notification.title}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'Уведомление уже существует: {notification.title}')
                    )

            else:
                self.stdout.write(
                    self.style.ERROR('Не найден менеджер. Сначала создайте менеджера командой: python manage.py create_manager')
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка при создании тестовых данных: {e}')
            )

        self.stdout.write(
            self.style.SUCCESS('Тестовые данные созданы успешно!')
        )