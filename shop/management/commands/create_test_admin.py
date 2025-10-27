from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Создает тестового администратора'

    def handle(self, *args, **options):
        email = 'testadmin@sanderstu.com'
        password = 'testadmin123'
        first_name = 'Test'
        last_name = 'Admin'

        # Проверяем, существует ли пользователь с таким email
        if User.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.WARNING(f'Пользователь с email {email} уже существует!')
            )
            return

        # Создаем нового пользователя
        user = User.objects.create_user(
            username=email,  # Используем email как username
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_staff=True,
            is_superuser=True,
            is_active=True
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Тестовый администратор создан!\n'
                f'Email: {email}\n'
                f'Пароль: {password}\n'
                f'Имя: {first_name} {last_name}'
            )
        )
