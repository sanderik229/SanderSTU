from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from . import views
from .api import CategoryViewSet, AdViewSet, PackageViewSet, OrderViewSet, ReviewViewSet, register

router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"ads", AdViewSet, basename="ad")
router.register(r"packages", PackageViewSet, basename="package")
router.register(r"orders", OrderViewSet, basename="order")
router.register(r"reviews", ReviewViewSet, basename="review")

urlpatterns = [
    # Pages
    path("", views.home_page, name="home"),
    path("buy/", views.buy_ads_page, name="buy_ads"),
    path("order/", views.order_ads_page, name="order_ads"),

    # REST API
    path("api/", include(router.urls)),
    path("api/auth/login/", obtain_auth_token, name="api_token_auth"),
    path("api/auth/register/", register, name="api_register"),
]


