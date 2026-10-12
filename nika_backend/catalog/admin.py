from django.contrib import admin
from django.utils.html import format_html

from .models import Category, Product, ProductImage, ProductVariant, Review


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'preview', 'alt_text', 'order', 'is_main']
    readonly_fields = ['preview']

    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:48px;border-radius:6px" />', obj.image.url)
        return '—'
    preview.short_description = 'پیش‌نمایش'


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 0
    fields = ['name', 'sku', 'price_override', 'stock', 'is_active']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'emoji', 'parent', 'is_active', 'order', 'product_count']
    list_editable = ['order', 'is_active']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'تعداد محصول'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'brand', 'price_display', 'stock_display', 'is_active', 'is_featured', 'created_at']
    list_filter = ['category', 'is_active', 'is_featured', 'brand']
    search_fields = ['name', 'sku', 'brand']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductVariantInline]
    list_editable = ['is_active', 'is_featured']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('اطلاعات اصلی', {'fields': ('name', 'slug', 'sku', 'category', 'brand')}),
        ('قیمت و موجودی', {'fields': ('price', 'compare_at_price', 'stock')}),
        ('محتوا', {'fields': ('description', 'specs')}),
        ('ارسال و مرجوعی', {'fields': ('shipping_note', 'return_policy')}),
        ('وضعیت', {'fields': ('is_active', 'is_featured')}),
        ('تاریخ‌ها', {'fields': ('created_at', 'updated_at')}),
    )

    def price_display(self, obj):
        if obj.is_on_sale:
            return format_html(
                '<span style="color:#C1594B;font-weight:700">{}٪ تخفیف</span><br><s>{}</s> → <b>{}</b>',
                obj.discount_percent, f'{obj.compare_at_price:,}', f'{obj.price:,}'
            )
        return f'{obj.price:,} ت'
    price_display.short_description = 'قیمت'

    def stock_display(self, obj):
        if obj.stock == 0:
            return format_html('<span style="color:#C1594B;font-weight:700">{}</span>', 'ناموجود')
        if obj.stock < 5:
            return format_html('<span style="color:#BE9A52;font-weight:700">{} عدد (کم)</span>', obj.stock)
        return obj.stock
    stock_display.short_description = 'موجودی'

    actions = ['deactivate_products', 'activate_products']

    def deactivate_products(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_products.short_description = 'غیرفعال کردن محصولات انتخاب‌شده'

    def activate_products(self, request, queryset):
        queryset.update(is_active=True)
    activate_products.short_description = 'فعال کردن محصولات انتخاب‌شده'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'rating']
    list_editable = ['is_approved']
    search_fields = ['product__name', 'user__phone']
