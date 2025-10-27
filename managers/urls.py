from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    ManagerViewSet, AdServiceViewSet, ManagerOrderViewSet, 
    WeeklyReportViewSet, NotificationViewSet
)
from .views import (
    manager_dashboard, manager_logout, manager_profile, get_bloggers,
    generate_weekly_report_pdf
)

router = DefaultRouter()
router.register(r'managers', ManagerViewSet)
router.register(r'services', AdServiceViewSet)
router.register(r'orders', ManagerOrderViewSet)
router.register(r'reports', WeeklyReportViewSet)
router.register(r'notifications', NotificationViewSet)

urlpatterns = [
    # Веб-интерфейс
    path('', manager_dashboard, name='manager_dashboard'),
    path('logout/', manager_logout, name='manager_logout'),
    path('profile/', manager_profile, name='manager_profile'),
    path('bloggers/', get_bloggers, name='get_bloggers'),
    path('reports/<int:report_id>/pdf/', generate_weekly_report_pdf, name='generate_report_pdf'),
    
    # API
    path('api/', include(router.urls)),
]
