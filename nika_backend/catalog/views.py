from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Category, Product, Review
from .serializers import (
    CategorySerializer, ProductListSerializer, ProductDetailSerializer, ReviewSerializer
)
from .filters import ProductFilter


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """GET /api/categories/  و  GET /api/categories/{slug}/"""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    lookup_field = 'slug'


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/products/                → لیست با فیلتر/جستجو/مرتب‌سازی (صفحه فروشگاه)
    GET /api/products/{slug}/         → جزئیات محصول
    GET /api/products/{slug}/similar/ → محصولات مشابه (همان دسته‌بندی)
    """
    queryset = Product.objects.filter(is_active=True).select_related('category').prefetch_related('images')
    filterset_class = ProductFilter
    lookup_field = 'slug'
    ordering_fields = ['price', 'created_at']

    def get_serializer_class(self):
        return ProductDetailSerializer if self.action == 'retrieve' else ProductListSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        ordering = self.request.query_params.get('ordering')
        # مرتب‌سازی طبق بخش ۵ سند: جدیدترین / ارزان‌ترین / گران‌ترین / محبوب‌ترین
        mapping = {
            'newest': '-created_at',
            'cheap': 'price',
            'expensive': '-price',
            'popular': '-is_featured',
        }
        qs = qs.order_by(mapping.get(ordering, '-created_at'))
        return qs

    @action(detail=True, methods=['get'])
    def similar(self, request, slug=None):
        product = self.get_object()
        similar_qs = Product.objects.filter(
            category=product.category, is_active=True
        ).exclude(id=product.id)[:4]
        serializer = ProductListSerializer(similar_qs, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def add_review(self, request, slug=None):
        """ثبت نظر و امتیاز کاربر (نیازمند ورود)."""
        product = self.get_object()
        serializer = ReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(product=product, user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
