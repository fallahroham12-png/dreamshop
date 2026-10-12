from django.urls import path

from .views import BannerListView, ApplyCouponView

urlpatterns = [
    path('banners/', BannerListView.as_view(), name='banner-list'),
    path('coupons/apply/', ApplyCouponView.as_view(), name='coupon-apply'),
]
