from django.urls import path

from .views import OrderCreateView, TrackOrderView

urlpatterns = [
    path('orders/', OrderCreateView.as_view(), name='order-create'),
    path('orders/track/', TrackOrderView.as_view(), name='order-track'),
]
