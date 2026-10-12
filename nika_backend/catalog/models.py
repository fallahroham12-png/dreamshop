from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from datetime import timedelta


class Category(models.Model):
    """دسته‌بندی محصولات (بخش ۱۴ سند — قابل مدیریت کامل از پنل)."""
    name = models.CharField('نام دسته‌بندی', max_length=80)
    slug = models.SlugField('اسلاگ', max_length=100, unique=True, blank=True)
    emoji = models.CharField('ایموجی نمایشی', max_length=8, blank=True, help_text='مثلاً 💄')
    image = models.ImageField('تصویر دسته‌بندی', upload_to='categories/', blank=True, null=True)
    parent = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='children', verbose_name='زیرمجموعه‌ی'
    )
    is_active = models.BooleanField('فعال', default=True)
    order = models.PositiveIntegerField('ترتیب نمایش', default=0)

    class Meta:
        verbose_name = 'دسته‌بندی'
        verbose_name_plural = 'دسته‌بندی‌ها'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)


class Product(models.Model):
    """محصول — فیلدهای اصلی طبق بخش ۱۴ و ۷ سند نیازمندی."""
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products', verbose_name='دسته‌بندی')
    name = models.CharField('نام محصول', max_length=200)
    slug = models.SlugField('اسلاگ', max_length=220, unique=True, blank=True)
    sku = models.CharField('کد کالا (SKU)', max_length=40, unique=True)
    brand = models.CharField('برند', max_length=80, blank=True)

    description = models.TextField('توضیحات محصول', blank=True)
    specs = models.JSONField('مشخصات فنی', default=dict, blank=True,
                              help_text='مثال: {"رنگ": "قرمز آجری", "حجم": "۳.۵ گرم", "نوع": "مات"}')

    price = models.PositiveIntegerField('قیمت (تومان)')
    compare_at_price = models.PositiveIntegerField(
        'قیمت قبل از تخفیف (تومان)', null=True, blank=True,
        help_text='در صورت خالی بودن، محصول تخفیف‌دار محسوب نمی‌شود.'
    )
    stock = models.PositiveIntegerField('موجودی', default=0)

    is_active = models.BooleanField('فعال (قابل نمایش)', default=True)
    is_featured = models.BooleanField('پرفروش / ویژه', default=False)

    shipping_note = models.CharField('روش ارسال', max_length=200, blank=True,
                                      default='ارسال طی ۲۴ تا ۴۸ ساعت کاری از طریق پست پیشتاز.')
    return_policy = models.CharField('شرایط مرجوعی', max_length=300, blank=True,
                                      default='امکان مرجوعی تا ۷ روز پس از دریافت کالا در صورت سالم بودن بسته‌بندی.')

    created_at = models.DateTimeField('تاریخ افزودن', auto_now_add=True)
    updated_at = models.DateTimeField('آخرین ویرایش', auto_now=True)

    class Meta:
        verbose_name = 'محصول'
        verbose_name_plural = 'محصولات'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_active', 'category']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    # ---- منطق تجاری که در فرانت‌اند/سریالایزر استفاده می‌شود ----
    @property
    def is_on_sale(self):
        return bool(self.compare_at_price and self.compare_at_price > self.price)

    @property
    def discount_percent(self):
        if not self.is_on_sale:
            return 0
        return round((1 - self.price / self.compare_at_price) * 100)

    @property
    def in_stock(self):
        return self.stock > 0

    @property
    def is_new(self):
        """محصول طی ۱۴ روز اخیر اضافه شده باشد، به‌عنوان «جدید» علامت‌گذاری می‌شود."""
        return self.created_at >= timezone.now() - timedelta(days=14)

    def reduce_stock(self, quantity):
        """کاهش موجودی هنگام ثبت سفارش — هرگز اجازه‌ی موجودی منفی نمی‌دهد (بخش ۱۵ و ۲۲ سند)."""
        if quantity > self.stock:
            raise ValueError(f'موجودی «{self.name}» کافی نیست.')
        self.stock -= quantity
        self.save(update_fields=['stock'])

    def restore_stock(self, quantity):
        """بازگرداندن موجودی در صورت لغو سفارش."""
        self.stock += quantity
        self.save(update_fields=['stock'])


class ProductImage(models.Model):
    """گالری تصاویر محصول (بخش ۷ سند)."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name='محصول')
    image = models.ImageField('تصویر', upload_to='products/')
    alt_text = models.CharField('متن جایگزین', max_length=150, blank=True)
    order = models.PositiveIntegerField('ترتیب نمایش', default=0)
    is_main = models.BooleanField('تصویر اصلی', default=False)

    class Meta:
        verbose_name = 'تصویر محصول'
        verbose_name_plural = 'تصاویر محصول'
        ordering = ['order']

    def __str__(self):
        return f'تصویر {self.product.name} #{self.order}'


class ProductVariant(models.Model):
    """
    تنوع محصول (رنگ/سایز) — طبق بخش ۲۴ سند، برای مواردی که موجودی هر گزینه
    باید جداگانه مدیریت شود (مثلاً اکسسوری با چند رنگ).
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants', verbose_name='محصول')
    name = models.CharField('نام گزینه', max_length=80, help_text='مثلاً: قرمز / سایز L')
    sku = models.CharField('کد کالا', max_length=40, unique=True)
    price_override = models.PositiveIntegerField('قیمت اختصاصی (تومان)', null=True, blank=True,
                                                   help_text='خالی بگذارید تا قیمت محصول اصلی استفاده شود.')
    stock = models.PositiveIntegerField('موجودی این گزینه', default=0)
    is_active = models.BooleanField('فعال', default=True)

    class Meta:
        verbose_name = 'تنوع محصول'
        verbose_name_plural = 'تنوع‌های محصول'

    def __str__(self):
        return f'{self.product.name} — {self.name}'

    @property
    def effective_price(self):
        return self.price_override or self.product.price


class Review(models.Model):
    """نظر و امتیاز کاربران — فاز دوم طبق بخش ۲۵ سند، اما ساختار از ابتدا آماده شده."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', verbose_name='محصول')
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='reviews', verbose_name='کاربر')
    rating = models.PositiveSmallIntegerField('امتیاز', validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField('متن نظر', blank=True)
    is_approved = models.BooleanField('تأیید شده توسط ادمین', default=False)
    created_at = models.DateTimeField('تاریخ ثبت', auto_now_add=True)

    class Meta:
        verbose_name = 'نظر کاربر'
        verbose_name_plural = 'نظرات کاربران'
        ordering = ['-created_at']
        unique_together = ('product', 'user')

    def __str__(self):
        return f'نظر {self.user} روی {self.product.name}'
