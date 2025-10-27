from django.shortcuts import redirect
from django.contrib import messages


class ManagerMiddleware:
    """Middleware для проверки прав доступа менеджера"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Проверяем доступ к панели менеджера
        if request.path.startswith('/manager/') and not request.path.startswith('/manager/api/'):
            # Если пользователь не аутентифицирован
            if not request.user.is_authenticated:
                messages.error(request, 'Необходимо войти в систему')
                return redirect('/login/')
            
            # Если пользователь не является менеджером
            if not hasattr(request.user, 'manager_profile'):
                messages.error(request, 'У вас нет прав доступа к панели менеджера')
                return redirect('/')
        
        response = self.get_response(request)
        return response
