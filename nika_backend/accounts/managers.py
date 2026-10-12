from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """مدیریت ساخت کاربر بر اساس شماره موبایل به‌جای ایمیل/یوزرنیم."""

    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError('شماره موبایل الزامی است.')
        user = self.model(phone=phone, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('ادمین باید is_staff=True داشته باشد.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('ادمین باید is_superuser=True داشته باشد.')

        return self.create_user(phone, password, **extra_fields)
