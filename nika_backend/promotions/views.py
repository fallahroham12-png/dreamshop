from rest_framework import generics, views, response, status

from .models import Banner
from .serializers import BannerSerializer, CouponApplySerializer


class BannerListView(generics.ListAPIView):
    """GET /api/banners/ — بنرهای فعال صفحه اصلی، قابل مدیریت کامل از پنل."""
    queryset = Banner.objects.filter(is_active=True)
    serializer_class = BannerSerializer


class ApplyCouponView(views.APIView):
    """POST /api/coupons/apply/  {code, subtotal} → بررسی اعتبار و محاسبه تخفیف بدون ثبت سفارش."""

    def post(self, request):
        serializer = CouponApplySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        coupon, discount_amount = serializer.apply()
        return response.Response({
            'valid': True,
            'code': coupon.code,
            'discount_amount': discount_amount,
        }, status=status.HTTP_200_OK)
