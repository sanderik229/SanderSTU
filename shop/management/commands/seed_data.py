from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from shop.models import Category, Ad, Package, Order, Review


class Command(BaseCommand):
    help = "Seed database with initial data and test users"

    def handle(self, *args, **options):
        User = get_user_model()

        # Users
        test_email = "test@example.com"
        test_password = "test12345"
        admin_email = "admin@example.com"
        admin_password = "admin12345"

        test_user, _ = User.objects.get_or_create(username=test_email, defaults={"email": test_email})
        if not test_user.has_usable_password():
            test_user.set_password(test_password)
            test_user.save()
        admin_user, _ = User.objects.get_or_create(username=admin_email, defaults={"email": admin_email, "is_staff": True, "is_superuser": True})
        if not admin_user.has_usable_password():
            admin_user.set_password(admin_password)
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()

        test_token, _ = Token.objects.get_or_create(user=test_user)
        admin_token, _ = Token.objects.get_or_create(user=admin_user)

        # Categories
        cat_banners, _ = Category.objects.get_or_create(name="Баннеры", slug="banners")
        cat_social, _ = Category.objects.get_or_create(name="Соцсети", slug="social")
        cat_email, _ = Category.objects.get_or_create(name="Email", slug="email")

        base_url = "http://127.0.0.1:8000"

        # Ads
        Ad.objects.get_or_create(
            title="Баннер на главной",
            category=cat_banners,
            defaults={
                "description": "Размещение баннера 728x90 на главной странице",
                "price": 15000,
                "popularity": 95,
                "image": f"{base_url}/static/shop/img/banner_main.svg",
                "is_active": True,
            },
        )
        Ad.objects.get_or_create(
            title="Пост в соцсетях",
            category=cat_social,
            defaults={
                "description": "Нативная интеграция в соцсетях",
                "price": 12000,
                "popularity": 88,
                "image": f"{base_url}/static/shop/img/social_post.svg",
                "is_active": True,
            },
        )
        Ad.objects.get_or_create(
            title="Реклама в рассылке",
            category=cat_email,
            defaults={
                "description": "Нативный блок в email-рассылке",
                "price": 9000,
                "popularity": 72,
                "image": f"{base_url}/static/shop/img/email_ad.svg",
                "is_active": True,
            },
        )

        # Packages
        Package.objects.get_or_create(name="Старт", defaults={"description": "Базовый набор каналов", "price": 5000, "is_active": True})
        Package.objects.get_or_create(name="Рост", defaults={"description": "Оптимизация и масштабирование", "price": 20000, "is_active": True})
        Package.objects.get_or_create(name="Лидер", defaults={"description": "Максимальная охватность", "price": 50000, "is_active": True})

        # Reviews
        ad1 = Ad.objects.filter(title="Баннер на главной").first()
        if ad1:
            Review.objects.get_or_create(user_name="Анна", rating=5, text="Трафик вырос на 35%.", ad=ad1)
            Review.objects.get_or_create(user_name="Игорь", rating=4, text="Прозрачные метрики и отчёты.", ad=ad1)

        self.stdout.write(self.style.SUCCESS("Seed completed"))
        self.stdout.write(f"Test user: {test_email} / {test_password}; token: {test_token.key}")
        self.stdout.write(f"Admin user: {admin_email} / {admin_password}; token: {admin_token.key}")


