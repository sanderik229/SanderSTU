from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
import os
import json
from .models import Manager, AdService, ManagerOrder, WeeklyReport, Notification
from bloggers.models import Blogger


@login_required
def public_orders(request):
    """Страница с заказами для пользователей"""
    return render(request, 'managers/public_orders.html')


@login_required
def manager_dashboard(request):
    """Главная страница панели менеджера"""
    # Проверяем, что пользователь является менеджером
    if not hasattr(request.user, 'manager_profile'):
        messages.error(request, 'У вас нет прав доступа к панели менеджера')
        return redirect('/')
    
    return render(request, 'managers/dashboard.html')


@login_required
@require_http_methods(["POST"])
def manager_logout(request):
    """Выход из системы менеджера"""
    logout(request)
    return JsonResponse({'success': True, 'redirect': '/'})


@login_required
def manager_profile(request):
    """Профиль менеджера"""
    if not hasattr(request.user, 'manager_profile'):
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    manager = request.user.manager_profile
    
    if request.method == 'GET':
        # Получаем список курируемых блоггеров
        managed_bloggers = Blogger.objects.filter(manager=manager)
        bloggers_data = [{
            'id': blogger.id,
            'name': blogger.name,
            'social_network': blogger.get_social_network_display(),
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
        
        response = JsonResponse(profile_data)
        response['Content-Type'] = 'application/json; charset=utf-8'
        return response
    
    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            
            # Обновляем данные пользователя
            if 'first_name' in data:
                manager.user.first_name = data['first_name']
            if 'last_name' in data:
                manager.user.last_name = data['last_name']
            if 'phone' in data:
                manager.phone = data['phone']
            if 'department' in data:
                manager.department = data['department']
            
            manager.user.save()
            manager.save()
            
            return JsonResponse({'message': 'Профиль успешно обновлен'}, status=200)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
def get_bloggers(request):
    """Получить список блоггеров для менеджера"""
    if not hasattr(request.user, 'manager_profile'):
        return JsonResponse({'error': 'Access denied'}, status=403)
    
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
    
    response = JsonResponse(bloggers_data, safe=False)
    response['Content-Type'] = 'application/json; charset=utf-8'
    return response


@login_required
def create_service(request):
    """Создать новую услугу"""
    if not hasattr(request.user, 'manager_profile'):
        return JsonResponse({'error': 'Access denied'}, status=403)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            manager = request.user.manager_profile

            # Получаем блоггера - он должен быть курируемым этим менеджером
            blogger_id = data.get('blogger_id')
            if not blogger_id:
                return JsonResponse({'error': 'Необходимо указать блоггера'}, status=400)
            
            try:
                blogger = Blogger.objects.get(id=blogger_id, manager=manager)
            except Blogger.DoesNotExist:
                return JsonResponse({'error': 'Блоггер не найден или не принадлежит вам'}, status=404)

            # Создаем услугу
            service = AdService.objects.create(
                manager=manager,
                name=data['name'],
                social_network=data['social_network'],
                price=data['price'],
                description=data.get('description', ''),
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

            response = JsonResponse(response_data)
            response['Content-Type'] = 'application/json; charset=utf-8'
            return response

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


def transliterate_russian(text):
    """Транслитерация русского текста в латиницу для PDF"""
    translit_dict = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'Yo',
        'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
        'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
        'Ф': 'F', 'Х': 'H', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Sch',
        'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya'
    }
    
    result = ''
    for char in text:
        result += translit_dict.get(char, char)
    return result


@login_required
def generate_weekly_report_pdf(request, report_id):
    """Генерация PDF отчета"""
    if not hasattr(request.user, 'manager_profile'):
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    try:
        report = WeeklyReport.objects.get(id=report_id, manager=request.user.manager_profile)
    except WeeklyReport.DoesNotExist:
        return JsonResponse({'error': 'Report not found'}, status=404)
    
    # Создаем PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    
    # Стили
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Times-Roman'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        fontName='Times-Roman'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=6,
        fontName='Times-Roman'
    )
    
    # Заголовок
    title = transliterate_russian(f"Еженедельный отчет менеджера")
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 20))
    
    # Информация о менеджере
    manager_name = transliterate_russian(f"Менеджер: {report.manager.user.get_full_name()}")
    story.append(Paragraph(manager_name, normal_style))
    
    period = transliterate_russian(f"Период: {report.week_start} - {report.week_end}")
    story.append(Paragraph(period, normal_style))
    story.append(Spacer(1, 20))
    
    # Основная статистика
    story.append(Paragraph(transliterate_russian("Основная статистика"), heading_style))
    
    stats_data = [
        [transliterate_russian("Показатель"), transliterate_russian("Значение")],
        [transliterate_russian("Общее количество заказов"), str(report.total_orders)],
        [transliterate_russian("Общая выручка"), f"{report.total_revenue} RUB"],
        [transliterate_russian("Активные услуги"), str(report.active_services)],
    ]
    
    stats_table = Table(stats_data)
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Times-Roman'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(stats_table)
    story.append(Spacer(1, 20))
    
    # Детальная информация по заказам
    story.append(Paragraph(transliterate_russian("Детальная информация по заказам"), heading_style))
    
    orders = ManagerOrder.objects.filter(
        manager=report.manager,
        created_at__date__range=[report.week_start, report.week_end]
    )
    
    if orders.exists():
        orders_data = [[
            transliterate_russian("ID заказа"),
            transliterate_russian("Тип"),
            transliterate_russian("Статус"),
            transliterate_russian("Клиент"),
            transliterate_russian("Бюджет")
        ]]
        
        for order in orders:
            orders_data.append([
                str(order.id),
                transliterate_russian(order.get_order_type_display()),
                transliterate_russian(order.get_status_display()),
                transliterate_russian(order.client_name or "N/A"),
                f"{order.budget or 0} RUB"
            ])
        
        orders_table = Table(orders_data)
        orders_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Times-Roman'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(orders_table)
    else:
        story.append(Paragraph(transliterate_russian("Заказов за указанный период не найдено"), normal_style))
    
    story.append(Spacer(1, 20))
    
    # Информация об услугах
    story.append(Paragraph(transliterate_russian("Активные услуги"), heading_style))
    
    services = AdService.objects.filter(manager=report.manager, is_active=True)
    
    if services.exists():
        services_data = [[
            transliterate_russian("Название"),
            transliterate_russian("Соцсеть"),
            transliterate_russian("Цена"),
            transliterate_russian("Блоггер")
        ]]
        
        for service in services:
            services_data.append([
                transliterate_russian(service.name),
                transliterate_russian(service.get_social_network_display()),
                f"{service.price} RUB",
                transliterate_russian(service.blogger.name)
            ])
        
        services_table = Table(services_data)
        services_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Times-Roman'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(services_table)
    else:
        story.append(Paragraph(transliterate_russian("Активных услуг не найдено"), normal_style))
    
    # Строим PDF
    doc.build(story)
    
    # Возвращаем PDF как ответ
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="weekly_report_{report_id}.pdf"'
    
    return response