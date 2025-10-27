from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from accounts.models import Profile
from ads.models import Order
from bloggers.models import AdOffer
from django.db.models import Count, Sum, Avg
from datetime import datetime, timedelta
from django.http import HttpResponse
import csv
import io
import json


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_stats(request):
    """Get admin dashboard statistics"""
    try:
        # Check if user is admin
        if not (request.user.is_staff or getattr(request.user.profile, 'role', 'user') == 'admin'):
            return Response({'detail': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)

        # Calculate stats
        total_orders = Order.objects.count()
        total_revenue = Order.objects.aggregate(
            total=Sum('offer__price')
        )['total'] or 0
        
        # Monthly stats
        month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_orders = Order.objects.filter(created_at__gte=month_start).count()
        
        # Active users (users with orders in last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        active_users = User.objects.filter(
            orders__created_at__gte=thirty_days_ago
        ).distinct().count()
        
        # Average order value
        avg_order = Order.objects.aggregate(
            avg=Avg('offer__price')
        )['avg'] or 0

        return Response({
            'totalRevenue': float(total_revenue),
            'monthlyOrders': monthly_orders,
            'activeUsers': active_users,
            'averageOrder': float(avg_order),
            'totalOrders': total_orders
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_orders(request):
    """Get all orders for admin panel"""
    try:
        # Check if user is admin
        if not (request.user.is_staff or getattr(request.user.profile, 'role', 'user') == 'admin'):
            return Response({'detail': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)

        # Get filter parameters
        status_filter = request.GET.get('status')
        search = request.GET.get('search')
        
        # Base queryset
        orders = Order.objects.select_related('user', 'offer', 'offer__blogger').all()
        
        # Apply filters
        if status_filter:
            orders = orders.filter(status=status_filter)
            
        if search:
            orders = orders.filter(
                full_name__icontains=search
            ) | orders.filter(
                user__username__icontains=search
            ) | orders.filter(
                offer__title__icontains=search
            )
        
        # Order by creation date (newest first)
        orders = orders.order_by('-created_at')
        
        # Serialize orders
        orders_data = []
        for order in orders:
            orders_data.append({
                'id': order.id,
                'full_name': order.full_name or (order.user.username if order.user else 'Неизвестно'),
                'email': order.email or (order.user.email if order.user else ''),
                'phone': order.phone or '',
                'offer': {
                    'id': order.offer.id if order.offer else None,
                    'title': order.offer.title if order.offer else 'Персональный заказ',
                    'price': float(order.offer.price) if order.offer else 0
                } if order.offer else None,
                'status': order.status,
                'order_type': order.order_type,
                'description': order.description or '',
                'created_at': order.created_at.isoformat(),
                'user': {
                    'id': order.user.id if order.user else None,
                    'username': order.user.username if order.user else None,
                    'email': order.user.email if order.user else None
                } if order.user else None
            })
        
        return Response({
            'results': orders_data,
            'count': len(orders_data)
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_users(request):
    """Get all users for admin panel"""
    try:
        # Check if user is admin
        if not (request.user.is_staff or getattr(request.user.profile, 'role', 'user') == 'admin'):
            return Response({'detail': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)

        users = User.objects.select_related('profile').all()
        
        users_data = []
        for user in users:
            users_data.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_active': user.is_active,
                'is_staff': user.is_staff,
                'date_joined': user.date_joined.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'profile': {
                    'full_name': user.profile.full_name if hasattr(user, 'profile') else '',
                    'role': user.profile.role if hasattr(user, 'profile') else 'user',
                    'birth_year': user.profile.birth_year if hasattr(user, 'profile') else None
                } if hasattr(user, 'profile') else {
                    'full_name': '',
                    'role': 'user',
                    'birth_year': None
                }
            })
        
        return Response({
            'results': users_data,
            'count': len(users_data)
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_order_status(request, order_id):
    """Update order status"""
    try:
        # Check if user is admin
        if not (request.user.is_staff or getattr(request.user.profile, 'role', 'user') == 'admin'):
            return Response({'detail': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)

        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({'detail': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get('status')
        if not new_status:
            return Response({'detail': 'Status is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate status
        valid_statuses = ['new', 'paid', 'in_progress', 'done', 'cancelled']
        if new_status not in valid_statuses:
            return Response({'detail': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

        order.status = new_status
        order.save()

        return Response({
            'id': order.id,
            'status': order.status,
            'message': 'Order status updated successfully'
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_user_status(request, user_id):
    """Toggle user active status"""
    try:
        # Check if user is admin
        if not (request.user.is_staff or getattr(request.user.profile, 'role', 'user') == 'admin'):
            return Response({'detail': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # Don't allow deactivating superusers
        if user.is_superuser and not user.is_active:
            return Response({'detail': 'Cannot deactivate superuser'}, status=status.HTTP_400_BAD_REQUEST)

        user.is_active = not user.is_active
        user.save()

        return Response({
            'id': user.id,
            'is_active': user.is_active,
            'message': f'User {"activated" if user.is_active else "deactivated"} successfully'
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_order(request, order_id):
    """Delete an order"""
    try:
        # Check if user is admin
        if not (request.user.is_staff or getattr(request.user.profile, 'role', 'user') == 'admin'):
            return Response({'detail': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)

        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({'detail': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

        order.delete()

        return Response({'message': 'Order deleted successfully'})
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_orders_csv(request):
    """Export orders to CSV"""
    try:
        # Check if user is admin
        if not (request.user.is_staff or getattr(request.user.profile, 'role', 'user') == 'admin'):
            return Response({'detail': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)

        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="orders.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['ID', 'Клиент', 'Email', 'Телефон', 'Услуга', 'Цена', 'Статус', 'Дата создания'])
        
        orders = Order.objects.all().order_by('-created_at')
        for order in orders:
            writer.writerow([
                order.id,
                order.full_name or order.user.username if order.user else 'Неизвестно',
                order.email or order.user.email if order.user else '',
                order.phone or '',
                order.offer.title if order.offer else 'Персональный заказ',
                order.offer.price if order.offer else '',
                order.status,
                order.created_at.strftime('%Y-%m-%d %H:%M')
            ])
        
        return response
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_users_csv(request):
    """Export users to CSV"""
    try:
        # Check if user is admin
        if not (request.user.is_staff or getattr(request.user.profile, 'role', 'user') == 'admin'):
            return Response({'detail': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)

        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="users.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['ID', 'Email', 'ФИО', 'Роль', 'Статус', 'Дата регистрации'])
        
        users = User.objects.all().order_by('-date_joined')
        for user in users:
            profile = getattr(user, 'profile', None)
            writer.writerow([
                user.id,
                user.email,
                profile.full_name if profile else '',
                profile.role if profile else 'user',
                'Активен' if user.is_active else 'Заблокирован',
                user.date_joined.strftime('%Y-%m-%d %H:%M')
            ])
        
        return response
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_services_csv(request):
    """Export services to CSV"""
    try:
        # Check if user is admin
        if not (request.user.is_staff or getattr(request.user.profile, 'role', 'user') == 'admin'):
            return Response({'detail': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)

        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="services.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['ID', 'Название', 'Блогер', 'Цена', 'Соцсеть', 'Описание', 'Статус'])
        
        offers = AdOffer.objects.all().order_by('-created_at')
        for offer in offers:
            writer.writerow([
                offer.id,
                offer.title,
                offer.blogger.name if offer.blogger else '',
                offer.price,
                offer.social_network,
                offer.description[:100] + '...' if len(offer.description) > 100 else offer.description,
                'Активен' if offer.is_active else 'Неактивен'
            ])
        
        return response
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_monthly_report(request):
    """Generate monthly PDF report"""
    try:
        # Check if user is admin
        if not (request.user.is_staff or getattr(request.user.profile, 'role', 'user') == 'admin'):
            return Response({'detail': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)

        # Get current month data
        now = datetime.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Calculate stats
        monthly_orders = Order.objects.filter(created_at__gte=month_start)
        total_revenue = monthly_orders.aggregate(total=Sum('offer__price'))['total'] or 0
        orders_count = monthly_orders.count()
        
        # Create simple text report (in production, use ReportLab for PDF)
        report_data = {
            'period': f"{month_start.strftime('%B %Y')}",
            'total_revenue': float(total_revenue),
            'orders_count': orders_count,
            'average_order': float(total_revenue / orders_count) if orders_count > 0 else 0,
            'generated_at': now.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        response = HttpResponse(json.dumps(report_data, ensure_ascii=False, indent=2), 
                               content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="monthly_report_{now.strftime("%Y_%m")}.json"'
        
        return response
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_user(request):
    """Create a new user"""
    try:
        # Check if user is admin
        if not (request.user.is_staff or getattr(request.user.profile, 'role', 'user') == 'admin'):
            return Response({'detail': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)

        email = request.data.get('email')
        password = request.data.get('password')
        full_name = request.data.get('full_name', '')
        role = request.data.get('role', 'user')

        if not email or not password:
            return Response({'detail': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if user already exists
        if User.objects.filter(email=email).exists():
            return Response({'detail': 'User with this email already exists'}, status=status.HTTP_400_BAD_REQUEST)

        # Create user
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password
        )

        # Create profile
        Profile.objects.create(
            user=user,
            full_name=full_name,
            role=role
        )

        return Response({
            'id': user.id,
            'email': user.email,
            'full_name': full_name,
            'role': role,
            'message': 'User created successfully'
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user(request, user_id):
    """Update user information"""
    try:
        # Check if user is admin
        if not (request.user.is_staff or getattr(request.user.profile, 'role', 'user') == 'admin'):
            return Response({'detail': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # Update user fields
        if 'email' in request.data:
            user.email = request.data['email']
            user.username = request.data['email']
        
        if 'password' in request.data and request.data['password']:
            user.set_password(request.data['password'])

        user.save()

        # Update profile
        profile, created = Profile.objects.get_or_create(user=user)
        if 'full_name' in request.data:
            profile.full_name = request.data['full_name']
        if 'role' in request.data:
            profile.role = request.data['role']
        profile.save()

        return Response({
            'id': user.id,
            'email': user.email,
            'full_name': profile.full_name,
            'role': profile.role,
            'message': 'User updated successfully'
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user(request, user_id):
    """Delete a user"""
    try:
        # Check if user is admin
        if not (request.user.is_staff or getattr(request.user.profile, 'role', 'user') == 'admin'):
            return Response({'detail': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # Don't allow deleting superuser
        if user.is_superuser:
            return Response({'detail': 'Cannot delete superuser'}, status=status.HTTP_400_BAD_REQUEST)

        user.delete()

        return Response({'message': 'User deleted successfully'})
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_service(request):
    """Create a new service (AdOffer)"""
    try:
        # Check if user is admin
        if not (request.user.is_staff or getattr(request.user.profile, 'role', 'user') == 'admin'):
            return Response({'detail': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)

        title = request.data.get('title')
        description = request.data.get('description', '')
        price = request.data.get('price')
        social_network = request.data.get('social_network', '')
        blogger_id = request.data.get('blogger_id')

        if not title or not price:
            return Response({'detail': 'Title and price are required'}, status=status.HTTP_400_BAD_REQUEST)

        # Get blogger if provided
        blogger = None
        if blogger_id:
            try:
                from bloggers.models import Blogger
                blogger = Blogger.objects.get(id=blogger_id)
            except Blogger.DoesNotExist:
                return Response({'detail': 'Blogger not found'}, status=status.HTTP_404_NOT_FOUND)

        # Create service
        service = AdOffer.objects.create(
            title=title,
            description=description,
            price=price,
            social_network=social_network,
            blogger=blogger,
            is_active=True
        )

        return Response({
            'id': service.id,
            'title': service.title,
            'description': service.description,
            'price': service.price,
            'social_network': service.social_network,
            'blogger': blogger.name if blogger else None,
            'message': 'Service created successfully'
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_service(request, service_id):
    """Update service information"""
    try:
        # Check if user is admin
        if not (request.user.is_staff or getattr(request.user.profile, 'role', 'user') == 'admin'):
            return Response({'detail': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)

        try:
            service = AdOffer.objects.get(id=service_id)
        except AdOffer.DoesNotExist:
            return Response({'detail': 'Service not found'}, status=status.HTTP_404_NOT_FOUND)

        # Update service fields
        if 'title' in request.data:
            service.title = request.data['title']
        if 'description' in request.data:
            service.description = request.data['description']
        if 'price' in request.data:
            service.price = request.data['price']
        if 'social_network' in request.data:
            service.social_network = request.data['social_network']
        if 'is_active' in request.data:
            service.is_active = request.data['is_active']

        service.save()

        return Response({
            'id': service.id,
            'title': service.title,
            'description': service.description,
            'price': service.price,
            'social_network': service.social_network,
            'is_active': service.is_active,
            'message': 'Service updated successfully'
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_service(request, service_id):
    """Delete a service"""
    try:
        # Check if user is admin
        if not (request.user.is_staff or getattr(request.user.profile, 'role', 'user') == 'admin'):
            return Response({'detail': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)

        try:
            service = AdOffer.objects.get(id=service_id)
        except AdOffer.DoesNotExist:
            return Response({'detail': 'Service not found'}, status=status.HTTP_404_NOT_FOUND)

        service.delete()

        return Response({'message': 'Service deleted successfully'})
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
