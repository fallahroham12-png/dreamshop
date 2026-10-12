from django.contrib import admin
from django.utils.html import format_html

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'variant', 'product_name', 'unit_price', 'quantity', 'total_price']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    پنل مدیریت سفارش‌ها — طبق بخش ۱۴ سند:
    نمایش شماره، مشتری، موبایل، محصولات، مبلغ، وضعیت پرداخت، وضعیت سفارش، آدرس، تاریخ
    و امکان تغییر وضعیت سفارش توسط ادمین.
    """
    list_display = [
        'order_number', 'full_name', 'phone', 'total_amount_display',
        'payment_status_display', 'status', 'created_at',
    ]
    list_filter = ['status', 'province', 'created_at']
    search_fields = ['order_number', 'full_name', 'phone']
    list_editable = ['status']
    inlines = [OrderItemInline]
    readonly_fields = [
        'order_number', 'subtotal', 'shipping_cost', 'discount_amount', 'total_amount',
        'payment_status', 'created_at', 'updated_at',
    ]

    fieldsets = (
        ('شناسه سفارش', {'fields': ('order_number', 'status', 'payment_status')}),
        ('اطلاعات مشتری', {'fields': ('user', 'full_name', 'phone')}),
        ('آدرس ارسال', {'fields': ('province', 'city', 'address', 'postal_code', 'note')}),
        ('مبالغ', {'fields': ('coupon', 'subtotal', 'shipping_cost', 'discount_amount', 'total_amount')}),
        ('تاریخ‌ها', {'fields': ('created_at', 'updated_at')}),
    )

    def total_amount_display(self, obj):
        return f'{obj.total_amount:,} ت'
    total_amount_display.short_description = 'مبلغ نهایی'

    def payment_status_display(self, obj):
        colors = {'موفق': '#5C8A6E', 'ناموفق': '#C1594B', 'در انتظار': '#BE9A52', 'ثبت‌نشده': '#9C8A82'}
        status = obj.payment_status
        color = colors.get(status, '#9C8A82')
        return format_html('<span style="color:{};font-weight:700">{}</span>', color, status)
    payment_status_display.short_description = 'وضعیت پرداخت'

    actions = ['cancel_orders']

    def cancel_orders(self, request, queryset):
        for order in queryset:
            order.mark_cancelled()
    cancel_orders.short_description = 'لغو سفارش‌های انتخاب‌شده و بازگرداندن موجودی'
