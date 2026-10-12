from rest_framework import serializers

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'variant', 'product_name', 'unit_price', 'quantity', 'total_price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_status = serializers.CharField(read_only=True)
    online_payment_amount = serializers.IntegerField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'full_name', 'phone', 'province', 'city', 'address', 'postal_code', 'note',
            'subtotal', 'shipping_cost', 'discount_amount', 'total_amount', 'online_payment_amount',
            'status', 'status_display', 'payment_status', 'items', 'created_at',
        ]
        read_only_fields = fields


class CartLineInputSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    variant_id = serializers.IntegerField(required=False, allow_null=True)
    quantity = serializers.IntegerField(min_value=1)


class OrderCreateSerializer(serializers.Serializer):
    """ورودی فرم ثبت سفارش — فیلدها دقیقاً طبق بخش ۱۰ سند نیازمندی."""
    full_name = serializers.CharField(max_length=120)
    phone = serializers.RegexField(r'^09\d{9}$', error_messages={'invalid': 'شماره موبایل نامعتبر است.'})
    province = serializers.CharField(max_length=60)
    city = serializers.CharField(max_length=60)
    address = serializers.CharField()
    postal_code = serializers.CharField(max_length=10)
    note = serializers.CharField(required=False, allow_blank=True, default='')
    coupon_code = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    items = CartLineInputSerializer(many=True)

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError('سبد خرید خالی است.')
        return value


class TrackOrderSerializer(serializers.Serializer):
    order_number = serializers.CharField()
    phone = serializers.RegexField(r'^09\d{9}$', error_messages={'invalid': 'شماره موبایل نامعتبر است.'})
