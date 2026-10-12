from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['order', 'amount_display', 'status', 'ref_id', 'created_at', 'paid_at']
    list_filter = ['status', 'gateway']
    search_fields = ['order__order_number', 'authority', 'ref_id']
    readonly_fields = ['order', 'gateway', 'amount', 'authority', 'ref_id', 'status', 'gateway_response', 'created_at', 'paid_at']

    def amount_display(self, obj):
        return f'{obj.amount:,} ت'
    amount_display.short_description = 'مبلغ'

    def has_add_permission(self, request):
        return False  # تراکنش‌ها فقط از طریق درگاه پرداخت ایجاد می‌شوند، نه دستی
