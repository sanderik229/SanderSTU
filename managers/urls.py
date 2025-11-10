from django.urls import path, include
from .views import (
    manager_dashboard, manager_logout, manager_profile, get_bloggers,
    generate_weekly_report_pdf, create_service, public_orders
)
from .api_views import (
    manager_profile_api, manager_profile_update_api, manager_bloggers_api,
    manager_services_api, manager_create_service_api, manager_reports_api,
    generate_report_api, manager_personal_orders_api, accept_order_api,
    reject_order_api, complete_order_api
)

urlpatterns = [
    # Веб-интерфейс
    path('', manager_dashboard, name='manager_dashboard'),
    path('logout/', manager_logout, name='manager_logout'),
    path('profile/', manager_profile, name='manager_profile'),
    path('bloggers/', get_bloggers, name='get_bloggers'),
    path('services/create/', create_service, name='create_service'),
    path('public-orders/', public_orders, name='public_orders'),
    path('reports/<int:report_id>/pdf/', generate_weekly_report_pdf, name='generate_report_pdf'),
    
    # API endpoints для JWT аутентификации
    path('api/profile/', manager_profile_api, name='manager_profile_api'),
    path('api/profile/update/', manager_profile_update_api, name='manager_profile_update_api'),
    path('api/bloggers/', manager_bloggers_api, name='manager_bloggers_api'),
    path('api/services/', manager_services_api, name='manager_services_api'),
    path('api/services/create/', manager_create_service_api, name='manager_create_service_api'),
    path('api/reports/', manager_reports_api, name='manager_reports_api'),
    path('api/reports/generate_report/', generate_report_api, name='generate_report_api'),
    path('api/orders/personal_orders/', manager_personal_orders_api, name='manager_personal_orders_api'),
    path('api/orders/<int:order_id>/accept/', accept_order_api, name='accept_order_api'),
    path('api/orders/<int:order_id>/reject/', reject_order_api, name='reject_order_api'),
    path('api/orders/<int:order_id>/complete/', complete_order_api, name='complete_order_api'),
]
