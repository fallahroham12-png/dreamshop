from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import RegisterView, LoginView, ProfileView, AddressViewSet

router = DefaultRouter()
router.register('addresses', AddressViewSet, basename='address')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth-register'),
    path('login/', LoginView.as_view(), name='auth-login'),
    path('profile/', ProfileView.as_view(), name='auth-profile'),
] + router.urls
