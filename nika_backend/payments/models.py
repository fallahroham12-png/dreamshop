from django.db import models

from orders.models import Order


class Payment(models.Model):
    """
    رکورد تراکنش پرداخت — طبق بخش ۱۱ و ۲۲ سند:
    - هیچ اطلاعات کارت بانکی در این مدل ذخیره نمی‌شود.
    - وضعیت «موفق» فقط بعد از تأیید واقعی از سمت درگاه ثبت می‌شود، نه صرفاً بازگشت کاربر.
    """
    STATUS_PENDING = 'pending'
    STATUS_SUCCESS = 'success'
    STATUS_FAILED = 'failed'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'در انتظار'),
        (STATUS_SUCCESS, 'موفق'),
        (STATUS_FAILED, 'ناموفق'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments', verbose_name='سفارش')
    gateway = models.CharField('درگاه', max_length=30, default='zarinpal')
    amount = models.PositiveIntegerField('مبلغ (تومان)')
    authority = models.CharField('کد Authority درگاه', max_length=100, blank=True)
    ref_id = models.CharField('کد رهگیری تراکنش (RefID)', max_length=100, blank=True)
    status = models.CharField('وضعیت', max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)
    gateway_response = models.JSONField('پاسخ خام درگاه', default=dict, blank=True)

    created_at = models.DateTimeField('تاریخ ایجاد', auto_now_add=True)
    paid_at = models.DateTimeField('تاریخ پرداخت موفق', null=True, blank=True)

    class Meta:
        verbose_name = 'تراکنش پرداخت'
        verbose_name_plural = 'تراکنش‌های پرداخت'
        ordering = ['-created_at']

    def __str__(self):
        return f'پرداخت {self.order.order_number} — {self.get_status_display()}'
