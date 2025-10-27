from django.contrib.auth.models import AnonymousUser
from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import get_user_model

User = get_user_model()


class JWTAuthenticationMiddleware(MiddlewareMixin):
    """
    Middleware для аутентификации пользователей через JWT токены в веб-запросах
    """
    
    def process_request(self, request):
        # Получаем токен из заголовка Authorization, cookies или специального заголовка
        token = None
        
        # Проверяем заголовок Authorization
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
        
        # Проверяем специальный заголовок для токенов из localStorage
        if not token:
            token = request.META.get('HTTP_X_ACCESS_TOKEN')
        
        # Проверяем cookies
        if not token:
            token = request.COOKIES.get('access_token')
        
        if token:
            try:
                # Валидируем токен
                access_token = AccessToken(token)
                user_id = access_token['user_id']
                user = User.objects.get(id=user_id)
                request.user = user
            except (InvalidToken, TokenError, User.DoesNotExist):
                request.user = AnonymousUser()
        else:
            request.user = AnonymousUser()
        
        return None
