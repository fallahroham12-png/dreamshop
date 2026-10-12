from django.contrib import admin
from django.utils.html import format_html

from .models import Coupon, Banner


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_type', 'value', 'min_amount', 'usage_display', 'validity_display', 'is_active']
    list_filter = ['discount_type', 'is_active']
    search_fields = ['code']
    list_editable = ['is_active']

    def usage_display(self, obj):
        return f'{obj.used_count} / {obj.usage_limit}'
    usage_display.short_description = 'میزان استفاده'

    def validity_display(self, obj):
        ok = obj.is_valid_now()
        color = '#5C8A6E' if ok else '#C1594B'
        label = 'معتبر' if ok else 'غیرمعتبر / منقضی'
        return format_html('<span style="color:{};font-weight:700">{}</span>', color, label)
    validity_display.short_description = 'وضعیت فعلی'


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'preview', 'order', 'is_active']
    list_editable = ['order', 'is_active']

    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:40px;border-radius:6px" />', obj.image.url)
        return '—'
    preview.short_description = 'پیش‌نمایش'
