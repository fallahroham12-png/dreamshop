from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, Address


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """پنل مدیریت کاربران — سفارشی‌شده برای ورود با موبایل به‌جای یوزرنیم."""
    ordering = ['-date_joined']
    list_display = ['phone', 'get_full_name', 'is_staff', 'is_active', 'date_joined']
    list_filter = ['is_staff', 'is_active']
    search_fields = ['phone', 'first_name', 'last_name', 'email']
    readonly_fields = ['date_joined']

    fieldsets = (
        (None, {'fields': ('phone', 'password')}),
        ('اطلاعات شخصی', {'fields': ('first_name', 'last_name', 'email')}),
        ('دسترسی‌ها', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('تاریخ‌ها', {'fields': ('date_joined',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'city', 'receiver_name', 'is_default']
    list_filter = ['province', 'is_default']
    search_fields = ['user__phone', 'receiver_name', 'city', 'full_address']
