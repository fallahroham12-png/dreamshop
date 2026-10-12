from django.db import models
from django.utils import timezone


class Coupon(models.Model):
    """کد تخفیف — بخش ۱۷ سند نیازمندی."""
    TYPE_PERCENT = 'percent'
    TYPE_FIXED = 'fixed'
    TYPE_CHOICES = [(TYPE_PERCENT, 'درصدی'), (TYPE_FIXED, 'مبلغ ثابت')]

    code = models.CharField('کد تخفیف', max_length=30, unique=True)
    discount_type = models.CharField('نوع تخفیف', max_length=10, choices=TYPE_CHOICES, default=TYPE_PERCENT)
    value = models.PositiveIntegerField('مقدار تخفیف', help_text='درصد (۱ تا ۱۰۰) یا مبلغ ثابت به تومان')
    min_amount = models.PositiveIntegerField('حداقل مبلغ خرید (تومان)', default=0)
    max_discount_amount = models.PositiveIntegerField(
        'سقف تخفیف (تومان)', null=True, blank=True,
        help_text='فقط برای تخفیف درصدی — خالی یعنی بدون سقف.'
    )
    start_date = models.DateTimeField('تاریخ شروع')
    end_date = models.DateTimeField('تاریخ پایان')
    usage_limit = models.PositiveIntegerField('تعداد استفاده مجاز', default=1)
    used_count = models.PositiveIntegerField('تعداد استفاده‌شده', default=0)
    is_active = models.BooleanField('فعال', default=True)

    class Meta:
        verbose_name = 'کد تخفیف'
        verbose_name_plural = 'کدهای تخفیف'
        ordering = ['-id']

    def __str__(self):
        return self.code

    def is_valid_now(self):
        now = timezone.now()
        return (
            self.is_active
            and self.start_date <= now <= self.end_date
            and self.used_count < self.usage_limit
        )

    def calculate_discount(self, subtotal):
        """محاسبه مبلغ تخفیف برای یک جمع سبد خرید مشخص. در صورت نامعتبر بودن، ۰ برمی‌گرداند."""
        if not self.is_valid_now() or subtotal < self.min_amount:
            return 0
        if self.discount_type == self.TYPE_PERCENT:
            amount = round(subtotal * self.value / 100)
            if self.max_discount_amount:
                amount = min(amount, self.max_discount_amount)
            return amount
        return min(self.value, subtotal)


class Banner(models.Model):
    """بنر صفحه اصلی — بخش ۱۸ سند نیازمندی."""
    title = models.CharField('عنوان', max_length=120)
    subtitle = models.CharField('متن فرعی', max_length=250, blank=True)
    image = models.ImageField('تصویر', upload_to='banners/', blank=True, null=True)
    link_url = models.CharField('لینک مقصد', max_length=300, blank=True)
    is_active = models.BooleanField('فعال', default=True)
    order = models.PositiveIntegerField('ترتیب نمایش', default=0)

    class Meta:
        verbose_name = 'بنر صفحه اصلی'
        verbose_name_plural = 'بنرهای صفحه اصلی'
        ordering = ['order']

    def __str__(self):
        return self.title
