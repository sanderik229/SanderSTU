from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('stats/', views.admin_stats, name='admin_stats'),
    path('orders/', views.admin_orders, name='admin_orders'),
    path('users/', views.admin_users, name='admin_users'),
    path('users/<int:user_id>/', views.get_user, name='get_user'),
    path('users/<int:user_id>/update/', views.update_user, name='update_user'),
    path('users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('users/<int:user_id>/toggle/', views.toggle_user_status, name='toggle_user_status'),
    path('users/create/', views.create_user, name='create_user'),
    path('orders/<int:order_id>/status/', views.update_order_status, name='update_order_status'),
    path('orders/<int:order_id>/delete/', views.delete_order, name='delete_order'),
    path('services/', views.admin_services, name='admin_services'),
    path('services/<int:service_id>/', views.get_service, name='get_service'),
    path('services/create/', views.create_service, name='create_service'),
    path('services/<int:service_id>/update/', views.update_service, name='update_service'),
    path('services/<int:service_id>/delete/', views.delete_service, name='delete_service'),
    path('export/orders/csv/', views.export_orders_csv, name='export_orders_csv'),
    path('export/users/csv/', views.export_users_csv, name='export_users_csv'),
    path('export/services/csv/', views.export_services_csv, name='export_services_csv'),
    path('reports/monthly/', views.generate_monthly_report, name='generate_monthly_report'),
]
