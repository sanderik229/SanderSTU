from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Создает нового администратора'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='Email администратора')
        parser.add_argument('--password', type=str, help='Пароль администратора')
        parser.add_argument('--first-name', type=str, help='Имя')
        parser.add_argument('--last-name', type=str, help='Фамилия')

    def handle(self, *args, **options):
        email = options.get('email') or input('Введите email: ')
        password = options.get('password') or input('Введите пароль: ')
        first_name = options.get('first_name') or input('Введите имя (необязательно): ')
        last_name = options.get('last_name') or input('Введите фамилию (необязательно): ')

        # Проверяем, существует ли пользователь с таким email
        if User.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.ERROR(f'Пользователь с email {email} уже существует!')
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
                f'Администратор успешно создан!\n'
                f'Email: {email}\n'
                f'Пароль: {password}\n'
                f'Имя: {first_name} {last_name}\n'
                f'Права: Суперпользователь + Персонал'
            )
        )
