from rest_framework import serializers

from .models import Banner, Coupon


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = ['id', 'title', 'subtitle', 'image', 'link_url', 'order']


class CouponApplySerializer(serializers.Serializer):
    """ورودی برای اعمال کد تخفیف روی سبد خرید."""
    code = serializers.CharField()
    subtotal = serializers.IntegerField(min_value=0)

    def validate_code(self, value):
        try:
            self._coupon = Coupon.objects.get(code__iexact=value.strip())
        except Coupon.DoesNotExist:
            raise serializers.ValidationError('کد تخفیف نامعتبر است.')
        return value

    def apply(self):
        coupon = self._coupon
        subtotal = self.validated_data['subtotal']
        if not coupon.is_valid_now():
            raise serializers.ValidationError({'code': 'این کد تخفیف منقضی شده یا غیرفعال است.'})
        if subtotal < coupon.min_amount:
            raise serializers.ValidationError({
                'code': f'حداقل مبلغ خرید برای این کد {coupon.min_amount:,} تومان است.'
            })
        return coupon, coupon.calculate_discount(subtotal)
