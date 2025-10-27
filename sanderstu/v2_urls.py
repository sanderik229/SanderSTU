from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from accounts.views import MeViewSet, register, UserAdminViewSet, update_profile
from bloggers.views import BloggerViewSet, AdOfferViewSet
from ads.views import CategoryViewSet, OrderViewSet
from payments.views import TransactionViewSet
from reviews.views import ReviewViewSet


router = DefaultRouter()
router.register(r"me", MeViewSet, basename="me")
router.register(r"admin/users", UserAdminViewSet, basename="admin-users")
router.register(r"bloggers", BloggerViewSet, basename="blogger")
router.register(r"offers", AdOfferViewSet, basename="offer")
router.register(r"categories", CategoryViewSet, basename="category2")
router.register(r"orders", OrderViewSet, basename="order2")
router.register(r"transactions", TransactionViewSet, basename="transaction")
router.register(r"reviews", ReviewViewSet, basename="review2")


urlpatterns = [
    path("profile/update/", update_profile, name="update_profile"),
    path("admin/", include("adminpanel.urls")),
    path("", include(router.urls)),
    path("auth/register/", register, name="register"),
    path("auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]


