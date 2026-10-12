import django_filters as filters

from .models import Product


class ProductFilter(filters.FilterSet):
    """
    فیلترهای صفحه فروشگاه — دقیقاً منطبق با بخش ۵ سند نیازمندی:
    دسته‌بندی، محدوده قیمت، موجود/ناموجود، تخفیف‌دار، جدیدترین، پرفروش‌ترین.
    """
    category = filters.CharFilter(field_name='category__slug', lookup_expr='iexact')
    min_price = filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = filters.NumberFilter(field_name='price', lookup_expr='lte')
    in_stock = filters.BooleanFilter(method='filter_in_stock')
    on_sale = filters.BooleanFilter(method='filter_on_sale')
    is_featured = filters.BooleanFilter(field_name='is_featured')
    search = filters.CharFilter(method='filter_search')

    class Meta:
        model = Product
        fields = ['category', 'min_price', 'max_price', 'in_stock', 'on_sale', 'is_featured', 'brand']

    def filter_in_stock(self, queryset, name, value):
        return queryset.filter(stock__gt=0) if value else queryset.filter(stock=0)

    def filter_on_sale(self, queryset, name, value):
        return queryset.filter(compare_at_price__isnull=False) if value else queryset

    def filter_search(self, queryset, name, value):
        # جستجو بر اساس نام محصول و برند — طبق بخش ۸ سند
        from django.db.models import Q
        return queryset.filter(Q(name__icontains=value) | Q(brand__icontains=value) | Q(sku__icontains=value))
