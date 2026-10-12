from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models

from .managers import UserManager

phone_validator = RegexValidator(
    regex=r'^09\d{9}$',
    message='شماره موبایل باید به فرمت 09xxxxxxxxx باشد.'
)


class User(AbstractBaseUser, PermissionsMixin):
    """
    کاربر فروشگاه — طبق بخش ۱۳ سند نیازمندی، ثبت‌نام با شماره موبایل انجام می‌شود.
    برای نسخه اول از رمز عبور ساده استفاده می‌شود؛ اتصال OTP در فاز بعد اضافه می‌شود
    (بدون نیاز به تغییر ساختار این مدل).
    """
    phone = models.CharField(
        'شماره موبایل', max_length=11, unique=True, validators=[phone_validator]
    )
    first_name = models.CharField('نام', max_length=60, blank=True)
    last_name = models.CharField('نام خانوادگی', max_length=60, blank=True)
    email = models.EmailField('ایمیل', blank=True)

    is_active = models.BooleanField('فعال', default=True)
    is_staff = models.BooleanField('دسترسی پنل مدیریت', default=False)
    date_joined = models.DateTimeField('تاریخ عضویت', auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'
        ordering = ['-date_joined']

    def __str__(self):
        full_name = f'{self.first_name} {self.last_name}'.strip()
        return full_name or self.phone

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'.strip() or self.phone

    def get_short_name(self):
        return self.first_name or self.phone


class Address(models.Model):
    """آدرس‌های ذخیره‌شده در حساب کاربری (بخش ۱۳ سند)."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses', verbose_name='کاربر')
    title = models.CharField('عنوان آدرس', max_length=60, help_text='مثلاً: خانه، محل کار', blank=True)
    receiver_name = models.CharField('نام گیرنده', max_length=120)
    receiver_phone = models.CharField('موبایل گیرنده', max_length=11, validators=[phone_validator])
    province = models.CharField('استان', max_length=60)
    city = models.CharField('شهر', max_length=60)
    full_address = models.TextField('آدرس کامل')
    postal_code = models.CharField('کد پستی', max_length=10)
    is_default = models.BooleanField('آدرس پیش‌فرض', default=False)
    created_at = models.DateTimeField('تاریخ ثبت', auto_now_add=True)

    class Meta:
        verbose_name = 'آدرس'
        verbose_name_plural = 'آدرس‌ها'
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f'{self.title or self.city} — {self.receiver_name}'
