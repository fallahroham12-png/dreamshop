from django.shortcuts import redirect
from rest_framework import views, status
from rest_framework.response import Response

from orders.models import Order
from .models import Payment
from .gateway import get_gateway


class StartPaymentView(views.APIView):
    """
    POST /api/payments/start/  {order_number}
    مرحله «پرداخت آنلاین» بخش ۱۱ سند — کاربر را به درگاه هدایت می‌کند.
    """

    def post(self, request):
        order_number = request.data.get('order_number')
        try:
            order = Order.objects.get(order_number=order_number, status=Order.STATUS_PENDING_PAYMENT)
        except Order.DoesNotExist:
            return Response({'detail': 'سفارش پیدا نشد یا قابل پرداخت نیست.'}, status=status.HTTP_404_NOT_FOUND)

        gateway = get_gateway()
        # هزینه ارسال آنلاین دریافت نمی‌شود؛ فقط مبلغ محصولات (منهای تخفیف) از طریق درگاه
        # پرداخت می‌شود و هزینه پست نقدی درب منزل از مشتری گرفته می‌شود.
        amount_rial = order.online_payment_amount * 10  # مبالغ فروشگاه به تومان، درگاه زرین‌پال ریالی است
        ok, authority_or_error, payment_url = gateway.request_payment(
            amount_rial=amount_rial,
            description=f'پرداخت سفارش {order.order_number}',
            mobile=order.phone,
        )

        payment = Payment.objects.create(
            order=order,
            amount=order.online_payment_amount,
            authority=authority_or_error if ok else '',
            status=Payment.STATUS_PENDING,
            gateway_response={} if ok else {'error': authority_or_error},
        )

        if not ok:
            payment.status = Payment.STATUS_FAILED
            payment.save(update_fields=['status'])
            return Response({'detail': f'اتصال به درگاه پرداخت ناموفق بود: {authority_or_error}'},
                             status=status.HTTP_502_BAD_GATEWAY)

        return Response({'payment_url': payment_url, 'authority': authority_or_error})


class VerifyPaymentView(views.APIView):
    """
    GET /api/payments/verify/?Authority=...&Status=OK
    Callback درگاه پرداخت. طبق بخش ۱۱ سند، وضعیت تراکنش هرگز صرفاً بر اساس
    بازگشت کاربر تعیین نمی‌شود — همیشه verify_payment واقعی با درگاه فراخوانی می‌شود.
    """

    def get(self, request):
        authority = request.query_params.get('Authority')
        gateway_status = request.query_params.get('Status')

        try:
            payment = Payment.objects.select_related('order').get(authority=authority, status=Payment.STATUS_PENDING)
        except Payment.DoesNotExist:
            return Response({'detail': 'تراکنش پیدا نشد.'}, status=status.HTTP_404_NOT_FOUND)

        order = payment.order

        if gateway_status != 'OK':
            payment.status = Payment.STATUS_FAILED
            payment.save(update_fields=['status'])
            return Response({'success': False, 'order_number': order.order_number, 'detail': 'پرداخت توسط کاربر لغو شد.'})

        gateway = get_gateway()
        ok, ref_id_or_error, raw = gateway.verify_payment(amount_rial=payment.amount * 10, authority=authority)

        if ok:
            payment.status = Payment.STATUS_SUCCESS
            payment.ref_id = ref_id_or_error
            payment.gateway_response = raw
            from django.utils import timezone
            payment.paid_at = timezone.now()
            payment.save()

            order.status = Order.STATUS_PAID
            order.save(update_fields=['status'])

            return Response({
                'success': True,
                'order_number': order.order_number,
                'ref_id': payment.ref_id,
                'amount': payment.amount,
            })

        payment.status = Payment.STATUS_FAILED
        payment.gateway_response = raw
        payment.save(update_fields=['status', 'gateway_response'])
        # موجودی رزروشده در سفارش، در صورت شکست قطعی پرداخت آزاد می‌شود
        order.release_stock()
        return Response({'success': False, 'order_number': order.order_number, 'detail': ref_id_or_error},
                         status=status.HTTP_402_PAYMENT_REQUIRED)
