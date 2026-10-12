"""
مسیرهای اصلی پروژه.
همه‌ی endpointهای API زیر پیشوند /api/ قرار دارند تا فرانت‌اند
(فایل HTML/JS موجود در پوشه frontend یا هر کلاینت دیگر) به‌سادگی به آن‌ها وصل شود.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, include


def api_root(request):
    return JsonResponse({
        'store': settings.STORE_NAME,
        'endpoints': {
            'categories': '/api/categories/',
            'products': '/api/products/',
            'banners': '/api/banners/',
            'apply_coupon': '/api/coupons/apply/',
            'create_order': '/api/orders/  (POST)',
            'track_order': '/api/orders/track/  (POST)',
            'start_payment': '/api/payments/start/  (POST)',
            'verify_payment': '/api/payments/verify/  (GET, callback درگاه)',
            'auth': '/api/auth/',
        }
    })


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api_root, name='api-root'),
    path('api/', include('catalog.urls')),
    path('api/', include('orders.urls')),
    path('api/', include('payments.urls')),
    path('api/', include('promotions.urls')),
    path('api/auth/', include('accounts.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
