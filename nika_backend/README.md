# بک‌اند فروشگاه نیکا (Django REST API)

این بک‌اند طبق سند نیازمندی‌های فروشگاه، با Django + Django REST Framework ساخته شده و برای اتصال به
فرانت‌اندی که قبلاً ساخته شده (فایل `index.html`) طراحی شده است.

## ساختار پروژه

```
config/         تنظیمات اصلی، urls.py
accounts/       کاربران (ورود با موبایل)، آدرس‌ها
catalog/        دسته‌بندی، محصول، تصاویر، تنوع محصول، نظرات
orders/         سبد خرید → سفارش، منطق کسر موجودی، پیگیری سفارش
payments/       اتصال به درگاه زرین‌پال + تأیید واقعی تراکنش
promotions/     کد تخفیف، بنر صفحه اصلی
core/           تنظیمات مشترک (برندینگ پنل مدیریت)
```

هر مدل، فیلد و پیام خطا به فارسی و با ارجاع به شماره بخش مربوطه در سند نیازمندی کامنت‌گذاری شده است.

## راه‌اندازی سریع (توسعه محلی)

```bash
python3 -m venv venv
source venv/bin/activate          # ویندوز: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env              # مقادیر را در صورت نیاز ویرایش کنید

python manage.py migrate
python manage.py seed_demo_data   # همان ۱۴ محصول نمونه‌ی فرانت‌اند را می‌سازد
python manage.py createsuperuser  # برای ورود به پنل مدیریت

python manage.py runserver
```

- پنل مدیریت: http://127.0.0.1:8000/admin/
- فهرست endpointها: http://127.0.0.1:8000/api/

در حالت DEBUG=True (پیش‌فرض) و بدون تنظیم متغیرهای DB_*، دیتابیس به‌صورت خودکار SQLite است —
نیازی به نصب PostgreSQL برای تست محلی نیست.

## Endpointهای اصلی API

| متد | مسیر | توضیح |
|---|---|---|
| GET | `/api/categories/` | لیست دسته‌بندی‌ها |
| GET | `/api/products/?category=&min_price=&max_price=&in_stock=&on_sale=&search=&ordering=` | لیست محصولات با فیلتر/جستجو/مرتب‌سازی |
| GET | `/api/products/{slug}/` | جزئیات محصول |
| GET | `/api/products/{slug}/similar/` | محصولات مشابه |
| GET | `/api/banners/` | بنرهای فعال صفحه اصلی |
| POST | `/api/coupons/apply/` | اعتبارسنجی کد تخفیف `{code, subtotal}` |
| POST | `/api/orders/` | ثبت سفارش از سبد خرید |
| POST | `/api/orders/track/` | پیگیری سفارش `{order_number, phone}` |
| POST | `/api/payments/start/` | شروع پرداخت `{order_number}` → لینک درگاه |
| GET | `/api/payments/verify/` | Callback زرین‌پال (تأیید واقعی تراکنش) |
| POST | `/api/auth/register/` | ثبت‌نام `{phone, password, first_name?}` |
| POST | `/api/auth/login/` | ورود → توکن |
| GET/PATCH | `/api/auth/profile/` | پروفایل کاربر (نیازمند هدر `Authorization: Token <key>`) |
| CRUD | `/api/auth/addresses/` | آدرس‌های کاربر |

مرتب‌سازی محصولات (`ordering`): `newest` / `cheap` / `expensive` / `popular` — دقیقاً منطبق با
گزینه‌های فرانت‌اند.

## نکات مهم پیاده‌سازی

- **مدیریت موجودی**: هنگام ثبت سفارش (`orders/services.py`) موجودی محصول داخل یک تراکنش اتمیک
  (`transaction.atomic` + `select_for_update`) کسر می‌شود تا در شرایط همزمانی بالا هرگز بیش از
  موجودی واقعی فروخته نشود. در صورت لغو سفارش یا شکست قطعی پرداخت، موجودی بازگردانده می‌شود.
- **پرداخت**: `payments/gateway.py` یک Wrapper برای زرین‌پال است. طبق سند نیازمندی، تأیید نهایی
  تراکنش همیشه با فراخوانی واقعی API درگاه انجام می‌شود، نه صرفاً با اعتماد به بازگشت کاربر از درگاه.
- **امنیت**: پسورد کاربران Hash می‌شود (مکانیزم پیش‌فرض Django)، هیچ اطلاعات کارت بانکی ذخیره
  نمی‌شود، CSRF/HSTS/SSL redirect در حالت Production فعال می‌شوند، و پیگیری سفارش با ترکیب
  شماره سفارش + موبایل محافظت شده تا کاربران به سفارش‌های یکدیگر دسترسی نداشته باشند.
- **قابلیت رشد**: مدل `ProductVariant` برای محصولاتی با چند رنگ/سایز از ابتدا آماده است، بنابراین
  رشد از ۱۰۰ به ۱۰۰۰ محصول نیازی به تغییر ساختار ندارد (طبق بخش ۲۵ سند).

## استقرار (Production)

1. `.env` را با مقادیر واقعی (`SECRET_KEY`، `DEBUG=False`، اطلاعات PostgreSQL، Merchant ID زرین‌پال) پر کنید.
2. `python manage.py collectstatic`
3. اجرا با Gunicorn پشت Nginx، طبق پیشنهاد سند نیازمندی:
   ```bash
   gunicorn config.wsgi:application --bind 0.0.0.0:8000
   ```
4. SSL/HTTPS را روی Nginx تنظیم کنید (Let's Encrypt رایگان است).

## گام بعدی برای اتصال فرانت‌اند

فایل `index.html` که قبلاً ساخته شده، فعلاً از داده‌ی درون‌حافظه‌ای JS استفاده می‌کند. برای اتصال واقعی:
1. آرایه‌ی `PRODUCTS` در `index.html` را با `fetch('/api/products/')` جایگزین کنید.
2. `submitOrder()` را به `POST /api/orders/` و سپس `POST /api/payments/start/` وصل کنید.
3. `doTrackOrder()` را به `POST /api/orders/track/` وصل کنید.
4. مقدار `CORS_ALLOWED_ORIGINS` در `.env` را با آدرس واقعی فرانت‌اند تنظیم کنید.

این مرحله (اتصال فرانت به بک‌اند) در فاز بعدی قابل انجام است.
