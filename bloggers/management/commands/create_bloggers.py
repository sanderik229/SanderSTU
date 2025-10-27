from django.core.management.base import BaseCommand
from bloggers.models import Blogger, AdOffer
from decimal import Decimal

class Command(BaseCommand):
    help = 'Добавляет блоггеров для тестирования функционала'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=5, help='Количество блоггеров для создания')

    def handle(self, *args, **options):
        count = options['count']
        
        bloggers_data = [
            {
                'name': 'Анна Петрова',
                'social_network': 'instagram',
                'topic': 'Fashion & Beauty',
                'audience_size': 75000
            },
            {
                'name': 'Максим Иванов',
                'social_network': 'youtube',
                'topic': 'Technology',
                'audience_size': 120000
            },
            {
                'name': 'Елена Смирнова',
                'social_network': 'tiktok',
                'topic': 'Lifestyle',
                'audience_size': 95000
            },
            {
                'name': 'Дмитрий Козлов',
                'social_network': 'vk',
                'topic': 'Gaming',
                'audience_size': 85000
            },
            {
                'name': 'Ольга Волкова',
                'social_network': 'telegram',
                'topic': 'Business',
                'audience_size': 60000
            }
        ]

        created_count = 0
        for i, blogger_data in enumerate(bloggers_data[:count]):
            blogger, created = Blogger.objects.get_or_create(
                name=blogger_data['name'],
                defaults={
                    'social_network': blogger_data['social_network'],
                    'topic': blogger_data['topic'],
                    'audience_size': blogger_data['audience_size']
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Создан блоггер: {blogger.name} ({blogger.social_network})')
                )
                
                # Создаем предложение для блоггера
                offer, offer_created = AdOffer.objects.get_or_create(
                    title=f"Реклама от {blogger.name}",
                    defaults={
                        'blogger': blogger,
                        'social_network': blogger.social_network,
                        'price': Decimal('15000.00'),
                        'description': f'Рекламное предложение от блоггера {blogger.name} в {blogger.get_social_network_display()}'
                    }
                )
                
                if offer_created:
                    self.stdout.write(
                        self.style.SUCCESS(f'  - Создано предложение: {offer.title} - {offer.price} руб.')
                    )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Блоггер уже существует: {blogger.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Создано {created_count} новых блоггеров из {count} запрошенных')
        )
