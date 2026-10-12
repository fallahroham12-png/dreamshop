import random
import string

from django.conf import settings
from django.db import models

from accounts.models import phone_validator
from catalog.models import Product, ProductVariant
from promotions.models import Coupon


def generate_order_number():
    """شماره سفارش خوانا برای پیگیری — بخش ۱۲ سند (مثال: NK-483920)."""
    digits = ''.join(random.choices(string.digits, k=6))
    return f'NK-{digits}'


class Order(models.Model):
    """
    سفارش — وضعیت‌ها دقیقاً طبق بخش ۱۲ سند نیازمندی:
    ثبت شده / در انتظار پرداخت / پرداخت شده / در حال آماده‌سازی / ارسال شده / تحویل داده شده / لغو شده
    """
    STATUS_REGISTERED = 'registered'
    STATUS_PENDING_PAYMENT = 'pending_payment'
    STATUS_PAID = 'paid'
    STATUS_PREPARING = 'preparing'
    STATUS_SHIPPED = 'shipped'
    STATUS_DELIVERED = 'delivered'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (STATUS_REGISTERED, 'ثبت شده'),
        (STATUS_PENDING_PAYMENT, 'در انتظار پرداخت'),
        (STATUS_PAID, 'پرداخت شده'),
        (STATUS_PREPARING, 'در حال آماده‌سازی'),
        (STATUS_SHIPPED, 'ارسال شده'),
        (STATUS_DELIVERED, 'تحویل داده شده'),
        (STATUS_CANCELLED, 'لغو شده'),
    ]

    order_number = models.CharField('شماره سفارش', max_length=20, unique=True, default=generate_order_number, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='orders', verbose_name='کاربر (در صورت ورود)'
    )

    # اطلاعات گیرنده — طبق بخش ۱۰ سند، حتی مهمان (بدون حساب کاربری) هم می‌تواند سفارش ثبت کند
    full_name = models.CharField('نام و نام خانوادگی', max_length=120)
    phone = models.CharField('شماره موبایل', max_length=11, validators=[phone_validator])
    province = models.CharField('استان', max_length=60)
    city = models.CharField('شهر', max_length=60)
    address = models.TextField('آدرس کامل')
    postal_code = models.CharField('کد پستی', max_length=10)
    note = models.TextField('توضیحات سفارش', blank=True)

    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders', verbose_name='کد تخفیف')

    subtotal = models.PositiveIntegerField('جمع محصولات (تومان)', default=0)
    shipping_cost = models.PositiveIntegerField('هزینه ارسال (تومان)', default=0)
    discount_amount = models.PositiveIntegerField('مبلغ تخفیف (تومان)', default=0)
    total_amount = models.PositiveIntegerField('مبلغ نهایی (تومان)', default=0)

    status = models.CharField('وضعیت سفارش', max_length=20, choices=STATUS_CHOICES, default=STATUS_REGISTERED)
    stock_reserved = models.BooleanField('موجودی کسر شده', default=False, editable=False)

    created_at = models.DateTimeField('تاریخ ثبت', auto_now_add=True)
    updated_at = models.DateTimeField('آخرین بروزرسانی', auto_now=True)

    class Meta:
        verbose_name = 'سفارش'
        verbose_name_plural = 'سفارش‌ها'
        ordering = ['-created_at']
        indexes = [models.Index(fields=['order_number', 'phone'])]

    def __str__(self):
        return f'{self.order_number} — {self.full_name}'

    @property
    def payment_status(self):
        """وضعیت پرداخت مشتق‌شده از آخرین رکورد Payment (بخش ۱۱ سند)."""
        last_payment = self.payments.order_by('-created_at').first()
        return last_payment.status if last_payment else 'ثبت‌نشده'

    @property
    def online_payment_amount(self):
        """
        مبلغی که واقعاً از طریق درگاه آنلاین دریافت می‌شود — یعنی جمع محصولات منهای تخفیف،
        بدون احتساب هزینه ارسال. هزینه ارسال طبق تصمیم فروشگاه، نقدی و درب منزل از مشتری
        دریافت می‌شود، نه از طریق درگاه.
        """
        return max(0, self.subtotal - self.discount_amount)

    def recalc_totals(self):
        self.subtotal = sum(item.unit_price * item.quantity for item in self.items.all())
        self.shipping_cost = settings.STORE_DEFAULT_SHIPPING_COST if self.subtotal > 0 else 0
        if self.coupon:
            self.discount_amount = self.coupon.calculate_discount(self.subtotal)
        # total_amount مبلغ کامل سفارش (محصولات + ارسال - تخفیف) برای ثبت و گزارش‌گیری است؛
        # مبلغی که واقعاً آنلاین پرداخت می‌شود توسط online_payment_amount مشخص می‌شود.
        self.total_amount = max(0, self.subtotal + self.shipping_cost - self.discount_amount)
        self.save(update_fields=['subtotal', 'shipping_cost', 'discount_amount', 'total_amount'])

    def reserve_stock(self):
        """
        کسر موجودی هنگام ثبت سفارش تا از فروش بیش از موجودی جلوگیری شود (بخش ۹، ۱۵، ۲۲ سند).
        این عملیات باید داخل transaction.atomic فراخوانی شود (نگاه کنید به orders/services.py).
        """
        if self.stock_reserved:
            return
        for item in self.items.select_related('product', 'variant'):
            if item.variant:
                if item.quantity > item.variant.stock:
                    raise ValueError(f'موجودی «{item.product.name} — {item.variant.name}» کافی نیست.')
                item.variant.stock -= item.quantity
                item.variant.save(update_fields=['stock'])
            else:
                item.product.reduce_stock(item.quantity)
        self.stock_reserved = True
        self.save(update_fields=['stock_reserved'])

    def release_stock(self):
        """بازگرداندن موجودی هنگام لغو سفارش."""
        if not self.stock_reserved:
            return
        for item in self.items.select_related('product', 'variant'):
            if item.variant:
                item.variant.stock += item.quantity
                item.variant.save(update_fields=['stock'])
            else:
                item.product.restore_stock(item.quantity)
        self.stock_reserved = False
        self.save(update_fields=['stock_reserved'])

    def mark_cancelled(self):
        self.release_stock()
        self.status = self.STATUS_CANCELLED
        self.save(update_fields=['status'])


class OrderItem(models.Model):
    """
    ردیف سفارش — نام و قیمت به‌صورت snapshot ذخیره می‌شود تا تغییرات بعدی
    قیمت محصول، سفارش‌های قبلی را دستکاری نکند.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='سفارش')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='order_items', verbose_name='محصول')
    variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT, null=True, blank=True, related_name='order_items', verbose_name='تنوع محصول')

    product_name = models.CharField('نام محصول (در زمان خرید)', max_length=200)
    unit_price = models.PositiveIntegerField('قیمت واحد (تومان)')
    quantity = models.PositiveIntegerField('تعداد', default=1)

    class Meta:
        verbose_name = 'ردیف سفارش'
        verbose_name_plural = 'ردیف‌های سفارش'

    def __str__(self):
        return f'{self.product_name} × {self.quantity}'

    @property
    def total_price(self):
        return self.unit_price * self.quantity

    def save(self, *args, **kwargs):
        if not self.unit_price:
            self.unit_price = self.variant.effective_price if self.variant else self.product.price
        if not self.product_name:
            self.product_name = self.product.name
        super().save(*args, **kwargs)
