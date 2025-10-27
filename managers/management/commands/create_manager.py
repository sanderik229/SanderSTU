from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from managers.models import Manager

User = get_user_model()


class Command(BaseCommand):
    help = 'Создать менеджера'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Email менеджера')
        parser.add_argument('password', type=str, help='Пароль менеджера')
        parser.add_argument('--first-name', type=str, default='', help='Имя')
        parser.add_argument('--last-name', type=str, default='', help='Фамилия')
        parser.add_argument('--phone', type=str, default='', help='Телефон')
        parser.add_argument('--department', type=str, default='', help='Отдел')

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']
        first_name = options['first_name']
        last_name = options['last_name']
        phone = options['phone']
        department = options['department']

        # Проверяем, существует ли пользователь
        if User.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.ERROR(f'Пользователь с email {email} уже существует')
            )
            return

        # Создаем пользователя
        user = User.objects.create_user(
            username=email,  # Используем email как username
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_staff=True  # Менеджер имеет права персонала
        )

        # Создаем профиль менеджера
        manager = Manager.objects.create(
            user=user,
            phone=phone,
            department=department
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Manager {user.get_full_name()} ({email}) created successfully!'
            )
        )
