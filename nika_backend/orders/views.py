from rest_framework import views, status
from rest_framework.response import Response

from .models import Order
from .serializers import OrderSerializer, OrderCreateSerializer, TrackOrderSerializer
from .services import create_order, OrderCreationError


class OrderCreateView(views.APIView):
    """
    POST /api/orders/
    ثبت سفارش نهایی از سبد خرید — طبق بخش ۱۰ سند.
    خروجی شامل شماره سفارش است تا مرحله بعد (پرداخت آنلاین) با آن آغاز شود.
    """

    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        items = data.pop('items')
        coupon_code = data.pop('coupon_code', None)

        user = request.user if request.user.is_authenticated else None
        try:
            order = create_order(shipping_info=data, cart_items=items, coupon_code=coupon_code, user=user)
        except OrderCreationError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class TrackOrderView(views.APIView):
    """
    POST /api/orders/track/  {order_number, phone}
    پیگیری سفارش با شماره سفارش و شماره موبایل — طبق بخش ۱۲ سند.
    عمداً از GET استفاده نشده تا شماره سفارش/موبایل در URL و لاگ سرور باقی نماند.
    """

    def post(self, request):
        serializer = TrackOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            order = Order.objects.get(
                order_number__iexact=serializer.validated_data['order_number'].strip(),
                phone=serializer.validated_data['phone'],
            )
        except Order.DoesNotExist:
            return Response({'detail': 'سفارشی با این مشخصات پیدا نشد.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(OrderSerializer(order).data)
