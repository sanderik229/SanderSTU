from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from managers.models import Manager, AdService, ManagerOrder
from bloggers.models import Blogger
import json

User = get_user_model()

def is_manager_user(user):
    """Проверяет, является ли пользователь менеджером"""
    return hasattr(user, 'manager_profile')

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def manager_profile_api(request):
    """API для получения профиля менеджера"""
    if not is_manager_user(request.user):
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    manager = request.user.manager_profile
    
    # Получаем список курируемых блоггеров
    managed_bloggers = Blogger.objects.filter(manager=manager)
    bloggers_data = [{
        'id': blogger.id,
        'name': blogger.name,
        'social_network': blogger.social_network,
        'topic': blogger.topic,
        'audience_size': blogger.audience_size
    } for blogger in managed_bloggers]

    profile_data = {
        'id': manager.id,
        'user_email': manager.user.email,
        'user_full_name': manager.user.get_full_name(),
        'first_name': manager.user.first_name,
        'last_name': manager.user.last_name,
        'phone': manager.phone,
        'department': manager.department,
        'hire_date': manager.hire_date,
        'is_active': manager.is_active,
        'active_orders_count': manager.active_orders_count,
        'managed_bloggers_count': manager.managed_bloggers_count,
        'managed_bloggers': bloggers_data,
        'created_at': manager.created_at,
        'updated_at': manager.updated_at
    }

    return Response(profile_data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def manager_profile_update_api(request):
    """API для обновления профиля менеджера"""
    if not is_manager_user(request.user):
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        manager = request.user.manager_profile
        
        # Обновляем данные пользователя
        if 'first_name' in request.data:
            manager.user.first_name = request.data['first_name']
        if 'last_name' in request.data:
            manager.user.last_name = request.data['last_name']
        if 'phone' in request.data:
            manager.phone = request.data['phone']
        if 'department' in request.data:
            manager.department = request.data['department']

        manager.user.save()
        manager.save()

        return Response({'message': 'Профиль успешно обновлен'}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def manager_bloggers_api(request):
    """API для получения блоггеров менеджера"""
    if not is_manager_user(request.user):
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    manager = request.user.manager_profile
    bloggers = Blogger.objects.filter(manager=manager)
    bloggers_data = [{
        'id': blogger.id,
        'name': blogger.name,
        'social_network': blogger.social_network,
        'topic': blogger.topic,
        'audience_size': blogger.audience_size,
        'manager_name': manager.user.get_full_name()
    } for blogger in bloggers]

    return Response(bloggers_data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def manager_services_api(request):
    """API для получения услуг менеджера"""
    if not is_manager_user(request.user):
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    manager = request.user.manager_profile
    services = AdService.objects.filter(manager=manager)
    services_data = [{
        'id': service.id,
        'name': service.name,
        'social_network': service.social_network,
        'price': float(service.price),
        'description': service.description,
        'blogger_name': service.blogger.name,
        'is_active': service.is_active,
        'created_at': service.created_at
    } for service in services]

    return Response(services_data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def manager_create_service_api(request):
    """API для создания услуги менеджером"""
    if not is_manager_user(request.user):
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        manager = request.user.manager_profile
        
        # Получаем блоггера - он должен быть курируемым этим менеджером
        blogger_id = request.data.get('blogger_id')
        if not blogger_id:
            return Response({'error': 'Необходимо указать блоггера'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            blogger = Blogger.objects.get(id=blogger_id, manager=manager)
        except Blogger.DoesNotExist:
            return Response({'error': 'Блоггер не найден или не принадлежит вам'}, status=status.HTTP_404_NOT_FOUND)

        # Создаем услугу
        service = AdService.objects.create(
            manager=manager,
            name=request.data['name'],
            social_network=request.data['social_network'],
            price=request.data['price'],
            description=request.data.get('description', ''),
            blogger=blogger
        )

        response_data = {
            'id': service.id,
            'name': service.name,
            'social_network': service.social_network,
            'price': float(service.price),
            'description': service.description,
            'blogger_name': blogger.name,
            'is_active': service.is_active
        }

        return Response(response_data, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)