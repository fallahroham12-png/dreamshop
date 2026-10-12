from rest_framework import serializers

from .models import Category, Product, ProductImage, ProductVariant, Review


class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.IntegerField(source='products.count', read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'emoji', 'image', 'parent', 'product_count']


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'order', 'is_main']


class ProductVariantSerializer(serializers.ModelSerializer):
    effective_price = serializers.IntegerField(read_only=True)

    class Meta:
        model = ProductVariant
        fields = ['id', 'name', 'sku', 'price_override', 'effective_price', 'stock', 'is_active']


class ReviewSerializer(serializers.ModelSerializer):
    user_display = serializers.CharField(source='user.get_short_name', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'user_display', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'user_display', 'created_at']


class ProductListSerializer(serializers.ModelSerializer):
    """سریالایزر سبک برای صفحه فروشگاه/شبکه محصولات (کارت محصول)."""
    category_name = serializers.CharField(source='category.name', read_only=True)
    main_image = serializers.SerializerMethodField()
    discount_percent = serializers.IntegerField(read_only=True)
    is_on_sale = serializers.BooleanField(read_only=True)
    in_stock = serializers.BooleanField(read_only=True)
    is_new = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'category_name', 'brand', 'price', 'compare_at_price',
            'discount_percent', 'is_on_sale', 'in_stock', 'stock', 'is_new', 'is_featured', 'main_image',
        ]

    def get_main_image(self, obj):
        img = obj.images.filter(is_main=True).first() or obj.images.first()
        if img and img.image:
            request = self.context.get('request')
            url = img.image.url
            return request.build_absolute_uri(url) if request else url
        return None


class ProductDetailSerializer(ProductListSerializer):
    """سریالایزر کامل برای صفحه محصول."""
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()

    class Meta(ProductListSerializer.Meta):
        fields = ProductListSerializer.Meta.fields + [
            'description', 'specs', 'shipping_note', 'return_policy',
            'images', 'variants', 'reviews', 'average_rating',
        ]

    def get_average_rating(self, obj):
        approved = obj.reviews.filter(is_approved=True)
        if not approved.exists():
            return None
        return round(sum(r.rating for r in approved) / approved.count(), 1)
