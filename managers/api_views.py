from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from managers.models import Manager, AdService, ManagerOrder, WeeklyReport
from bloggers.models import Blogger
from datetime import datetime, timedelta
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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def manager_reports_api(request):
    """API для получения отчетов менеджера"""
    if not is_manager_user(request.user):
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    manager = request.user.manager_profile
    reports = WeeklyReport.objects.filter(manager=manager).order_by('-created_at')
    
    reports_data = [{
        'id': report.id,
        'week_start': str(report.week_start),
        'week_end': str(report.week_end),
        'total_orders': report.total_orders,
        'total_revenue': float(report.total_revenue),
        'active_services': report.active_services,
        'created_at': report.created_at.isoformat() if report.created_at else None
    } for report in reports]

    return Response(reports_data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_report_api(request):
    """API для генерации отчета"""
    if not is_manager_user(request.user):
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        manager = request.user.manager_profile
        
        week_start = request.data.get('week_start')
        week_end = request.data.get('week_end')
        
        if not week_start or not week_end:
            return Response({'error': 'Необходимо указать даты начала и конца недели'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Получаем или создаем отчет
        report, created = WeeklyReport.objects.get_or_create(
            manager=manager,
            week_start=week_start,
            week_end=week_end,
            defaults={
                'total_orders': 0,
                'total_revenue': 0,
                'active_services': 0
            }
        )
        
        # Подсчитываем статистику
        from django.db.models import Count, Sum
        
        # Подсчет заказов за период
        orders = ManagerOrder.objects.filter(
            manager=manager,
            created_at__date__gte=week_start,
            created_at__date__lte=week_end
        )
        
        report.total_orders = orders.count()
        report.total_revenue = sum(order.budget or 0 for order in orders)
        
        # Подсчет активных услуг
        report.active_services = AdService.objects.filter(
            manager=manager,
            is_active=True
        ).count()
        
        report.save()
        
        # Возвращаем данные отчета
        report_data = {
            'id': report.id,
            'week_start': str(report.week_start),
            'week_end': str(report.week_end),
            'total_orders': report.total_orders,
            'total_revenue': float(report.total_revenue),
            'active_services': report.active_services,
            'created_at': report.created_at.isoformat() if report.created_at else None
        }
        
        return Response(report_data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        print(f"Error in generate_report_api: {e}")
        import traceback
        traceback.print_exc()
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def manager_personal_orders_api(request):
    """API для получения персональных заказов менеджера"""
    if not is_manager_user(request.user):
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    manager = request.user.manager_profile
    orders = ManagerOrder.objects.filter(
        manager=manager,
        order_type='personal'
    ).order_by('-created_at')
    
    orders_data = [{
        'id': order.id,
        'client_name': order.client_name or 'Не указано',
        'client_email': order.client_email or 'Не указано',
        'client_phone': order.client_phone or 'Не указано',
        'service_description': order.service_description or 'Не указано',
        'budget': float(order.budget) if order.budget else 0,
        'status': order.status,
        'created_at': order.created_at.isoformat() if hasattr(order.created_at, 'isoformat') else str(order.created_at)
    } for order in orders]

    return Response(orders_data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def accept_order_api(request, order_id):
    """API для принятия заказа менеджером"""
    if not is_manager_user(request.user):
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        manager = request.user.manager_profile
        order = ManagerOrder.objects.get(id=order_id, manager=manager)
        
        if order.status != 'new':
            return Response({'error': 'Заказ уже обработан'}, status=status.HTTP_400_BAD_REQUEST)
        
        order.status = 'accepted'
        order.save()
        
        return Response({
            'success': True,
            'message': 'Заказ успешно принят',
            'order': {
                'id': order.id,
                'status': order.status
            }
        })
        
    except ManagerOrder.DoesNotExist:
        return Response({'error': 'Заказ не найден'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_order_api(request, order_id):
    """API для отклонения заказа менеджером"""
    if not is_manager_user(request.user):
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        manager = request.user.manager_profile
        order = ManagerOrder.objects.get(id=order_id, manager=manager)
        
        if order.status != 'new':
            return Response({'error': 'Заказ уже обработан'}, status=status.HTTP_400_BAD_REQUEST)
        
        order.status = 'cancelled'
        order.save()
        
        return Response({
            'success': True,
            'message': 'Заказ отклонен',
            'order': {
                'id': order.id,
                'status': order.status
            }
        })
        
    except ManagerOrder.DoesNotExist:
        return Response({'error': 'Заказ не найден'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_order_api(request, order_id):
    """API для завершения заказа менеджером"""
    if not is_manager_user(request.user):
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        manager = request.user.manager_profile
        order = ManagerOrder.objects.get(id=order_id, manager=manager)
        
        if order.status not in ['accepted', 'in_progress']:
            return Response({'error': 'Заказ не может быть завершен'}, status=status.HTTP_400_BAD_REQUEST)
        
        order.status = 'completed'
        order.save()
        
        return Response({
            'success': True,
            'message': 'Заказ успешно завершен',
            'order': {
                'id': order.id,
                'status': order.status
            }
        })
        
    except ManagerOrder.DoesNotExist:
        return Response({'error': 'Заказ не найден'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)