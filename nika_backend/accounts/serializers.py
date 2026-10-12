from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from .models import User, Address


class RegisterSerializer(serializers.ModelSerializer):
    """
    ثبت‌نام با شماره موبایل — طبق بخش ۱۳ سند.
    نسخه اول بدون OTP (با رمز عبور ساده) پیاده شده؛ اتصال OTP در فاز بعد
    فقط نیازمند جایگزینی این سریالایزر است، نه تغییر مدل User.
    """
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['phone', 'first_name', 'last_name', 'password']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    phone = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(phone=attrs['phone'], password=attrs['password'])
        if not user:
            raise serializers.ValidationError('شماره موبایل یا رمز عبور اشتباه است.')
        if not user.is_active:
            raise serializers.ValidationError('این حساب کاربری غیرفعال است.')
        attrs['user'] = user
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'phone', 'first_name', 'last_name', 'email', 'date_joined']
        read_only_fields = ['id', 'phone', 'date_joined']


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            'id', 'title', 'receiver_name', 'receiver_phone',
            'province', 'city', 'full_address', 'postal_code', 'is_default',
        ]

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
