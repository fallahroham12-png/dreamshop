"""
منطق تجاری ثبت سفارش — جدا از views برای قابلیت تست و استفاده مجدد.
"""
from django.db import transaction

from catalog.models import Product, ProductVariant
from promotions.models import Coupon
from .models import Order, OrderItem


class OrderCreationError(Exception):
    """خطای قابل‌نمایش به کاربر (مثلاً کمبود موجودی)."""
    pass


@transaction.atomic
def create_order(*, shipping_info: dict, cart_items: list, coupon_code: str | None, user=None) -> Order:
    """
    ورودی cart_items: [{'product_id': int, 'variant_id': int|None, 'quantity': int}, ...]
    خروجی: شیء Order ساخته‌شده با موجودی کسرشده و مبالغ محاسبه‌شده.
    از transaction.atomic استفاده می‌شود تا در صورت بروز خطا (مثلاً کمبود موجودی)،
    هیچ سفارش ناقصی در دیتابیس باقی نماند.
    """
    if not cart_items:
        raise OrderCreationError('سبد خرید خالی است.')

    order = Order.objects.create(user=user, **shipping_info)

    for line in cart_items:
        product = Product.objects.select_for_update().get(id=line['product_id'], is_active=True)
        variant = None
        if line.get('variant_id'):
            variant = ProductVariant.objects.select_for_update().get(id=line['variant_id'], product=product)
            available = variant.stock
        else:
            available = product.stock

        quantity = int(line['quantity'])
        if quantity < 1:
            raise OrderCreationError(f'تعداد نامعتبر برای «{product.name}».')
        if quantity > available:
            raise OrderCreationError(f'موجودی «{product.name}» کافی نیست (موجودی فعلی: {available}).')

        OrderItem.objects.create(
            order=order,
            product=product,
            variant=variant,
            product_name=product.name,
            unit_price=(variant.effective_price if variant else product.price),
            quantity=quantity,
        )

    if coupon_code:
        try:
            order.coupon = Coupon.objects.get(code__iexact=coupon_code.strip())
        except Coupon.DoesNotExist:
            pass  # کد نامعتبر بی‌صدا نادیده گرفته می‌شود؛ محاسبه تخفیف صفر خواهد بود

    order.recalc_totals()

    try:
        order.reserve_stock()
    except ValueError as exc:
        raise OrderCreationError(str(exc))

    order.status = Order.STATUS_PENDING_PAYMENT
    order.save(update_fields=['status', 'coupon'])
    return order
