from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from managers.models import Manager

User = get_user_model()

class Command(BaseCommand):
    help = 'Исправляет данные менеджера с правильной кодировкой UTF-8'

    def handle(self, *args, **options):
        try:
            # Находим менеджера
            manager = Manager.objects.first()
            if not manager:
                self.stdout.write(
                    self.style.ERROR('Менеджер не найден')
                )
                return

            user = manager.user
            
            # Исправляем данные пользователя
            user.first_name = "Иван"
            user.last_name = "Менеджеров"
            user.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'Данные менеджера исправлены: {user.first_name} {user.last_name}')
            )
            
            # Проверяем результат
            self.stdout.write(f'Email: {user.email}')
            self.stdout.write(f'Username: {user.username}')
            self.stdout.write(f'Full name: {user.get_full_name()}')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка при исправлении данных: {e}')
            )
