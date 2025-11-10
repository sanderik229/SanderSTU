from django.test import TestCase
from django.contrib.auth.models import User
from django.db import IntegrityError
from .models import Profile


class ProfileModelTest(TestCase):
    """Unit-тесты для модели Profile"""
    
    def setUp(self):
        """Настройка тестовых данных"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_profile(self):
        """Тест создания профиля пользователя"""
        profile = Profile.objects.create(
            user=self.user,
            full_name='John Doe',
            birth_year=1990,
            role='user'
        )
        
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.full_name, 'John Doe')
        self.assertEqual(profile.birth_year, 1990)
        self.assertEqual(profile.role, 'user')
        self.assertFalse(profile.card_last4)  # Пустая строка
        
        print("✓ Профиль успешно создан")
    
    def test_profile_str_representation(self):
        """Тест строкового представления профиля"""
        profile = Profile.objects.create(
            user=self.user,
            full_name='Jane Smith'
        )
        
        expected_str = f"{profile.full_name} ({profile.user.username})"
        self.assertEqual(str(profile), expected_str)
        
        print(f"✓ Строковое представление: {str(profile)}")
    
    def test_profile_role_choices(self):
        """Тест валидных ролей профиля"""
        valid_roles = ['user', 'admin', 'manager']
        
        for role in valid_roles:
            profile = Profile.objects.create(
                user=User.objects.create_user(
                    username=f'user_{role}',
                    email=f'{role}@example.com'
                ),
                full_name=f'User {role}',
                role=role
            )
            self.assertEqual(profile.role, role)
            print(f"✓ Роль '{role}' успешно установлена")
    
    def test_profile_one_to_one_relationship(self):
        """Тест связи один-к-одному между User и Profile"""
        profile = Profile.objects.create(
            user=self.user,
            full_name='Test User'
        )
        
        # Проверяем обратную связь от User
        self.assertEqual(profile, self.user.profile)
        
        # Попытка создать второй профиль для того же пользователя должна вызвать ошибку
        with self.assertRaises(IntegrityError):
            Profile.objects.create(
                user=self.user,
                full_name='Duplicate Profile'
            )
        
        print("✓ Связь один-к-одному работает корректно")
    
    def test_profile_default_role(self):
        """Тест значения по умолчанию для роли"""
        profile = Profile.objects.create(
            user=self.user,
            full_name='Default User'
        )
        
        self.assertEqual(profile.role, 'user')
        print("✓ Значение по умолчанию для роли установлено")
    
    def test_profile_card_last4_optional(self):
        """Тест опционального поля card_last4"""
        # Профиль без карты
        profile1 = Profile.objects.create(
            user=self.user,
            full_name='User Without Card'
        )
        self.assertEqual(profile1.card_last4, '')
        print("✓ Профиль без карты создан")
        
        # Профиль с картой
        user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com'
        )
        profile2 = Profile.objects.create(
            user=user2,
            full_name='User With Card',
            card_last4='1234'
        )
        self.assertEqual(profile2.card_last4, '1234')
        print("✓ Профиль с картой создан")
    
    def test_profile_update(self):
        """Тест обновления профиля"""
        profile = Profile.objects.create(
            user=self.user,
            full_name='Original Name',
            birth_year=1985,
            role='user'
        )
        
        # Обновляем профиль
        profile.full_name = 'Updated Name'
        profile.birth_year = 1995
        profile.role = 'admin'
        profile.save()
        
        updated_profile = Profile.objects.get(id=profile.id)
        self.assertEqual(updated_profile.full_name, 'Updated Name')
        self.assertEqual(updated_profile.birth_year, 1995)
        self.assertEqual(updated_profile.role, 'admin')
        
        print("✓ Профиль успешно обновлен")
    
    def test_profile_with_none_birth_year(self):
        """Тест профиля с None в birth_year"""
        profile = Profile.objects.create(
            user=self.user,
            full_name='User No Birth Year',
            birth_year=None
        )
        
        self.assertIsNone(profile.birth_year)
        print("✓ Профиль с None в birth_year создан")


class ProfileIntegrationTest(TestCase):
    """Интеграционные тесты для Profile"""
    
    def setUp(self):
        """Настройка данных для интеграционных тестов"""
        self.users_data = [
            {
                'username': 'user1',
                'email': 'user1@example.com',
                'full_name': 'User One',
                'role': 'user'
            },
            {
                'username': 'admin1',
                'email': 'admin@example.com',
                'full_name': 'Admin User',
                'role': 'admin'
            },
            {
                'username': 'manager1',
                'email': 'manager@example.com',
                'full_name': 'Manager User',
                'role': 'manager'
            },
        ]
        
        for user_data in self.users_data:
            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['email']
            )
            Profile.objects.create(
                user=user,
                full_name=user_data['full_name'],
                role=user_data['role']
            )
    
    def test_get_all_profiles(self):
        """Тест получения всех профилей"""
        profiles = Profile.objects.all()
        self.assertEqual(profiles.count(), 3)
        print(f"✓ Получено профилей: {profiles.count()}")
    
    def test_filter_profiles_by_role(self):
        """Тест фильтрации профилей по роли"""
        user_profiles = Profile.objects.filter(role='user')
        admin_profiles = Profile.objects.filter(role='admin')
        manager_profiles = Profile.objects.filter(role='manager')
        
        self.assertEqual(user_profiles.count(), 1)
        self.assertEqual(admin_profiles.count(), 1)
        self.assertEqual(manager_profiles.count(), 1)
        
        print(f"✓ Фильтрация работает: {user_profiles.count()} user, {admin_profiles.count()} admin, {manager_profiles.count()} manager")
    
    def test_profile_user_cascade_delete(self):
        """Тест каскадного удаления профиля при удалении пользователя"""
        user = User.objects.get(username='user1')
        profile = user.profile
        
        self.assertTrue(Profile.objects.filter(id=profile.id).exists())
        
        # Удаляем пользователя
        user.delete()
        
        # Профиль должен быть удален автоматически
        self.assertFalse(Profile.objects.filter(id=profile.id).exists())
        print("✓ Каскадное удаление профиля работает")
    
    def tearDown(self):
        """Очистка после тестов"""
        print("\n--- Тесты завершены ---\n")


# Команда для запуска тестов:
# python manage.py test accounts.tests.ProfileModelTest
# python manage.py test accounts.tests.ProfileIntegrationTest
# python manage.py test accounts --verbosity=2

