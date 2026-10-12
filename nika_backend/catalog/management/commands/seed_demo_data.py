from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from catalog.models import Category, Product
from promotions.models import Coupon, Banner


class Command(BaseCommand):
    help = 'داده‌های نمونه فروشگاه نیکا را می‌سازد (همان محصولات نمایش داده‌شده در پروتوتایپ فرانت‌اند).'

    def handle(self, *args, **options):
        makeup, _ = Category.objects.get_or_create(
            slug='makeup', defaults={'name': 'لوازم آرایشی', 'emoji': '💄', 'order': 1}
        )
        accessory, _ = Category.objects.get_or_create(
            slug='accessory', defaults={'name': 'اکسسوری', 'emoji': '💍', 'order': 2}
        )

        products = [
            dict(name='رژ لب مات مخملی شماره ۰۵', category=makeup, brand='نیکا بیوتی', sku='NK-001',
                 price=285000, compare_at_price=340000, stock=12, is_featured=True,
                 description='رژ لبی با پوشش کامل و ماندگاری بالا که بدون خشک کردن لب، رنگی یکنواخت و مخملی می‌دهد.',
                 specs={'رنگ': 'قرمز آجری', 'حجم': '۳.۵ گرم', 'نوع': 'مات'}),
            dict(name='پالت سایه چشم ۱۲ رنگ نچرال', category=makeup, brand='لومیا', sku='NK-002',
                 price=410000, compare_at_price=None, stock=8, is_featured=True,
                 description='پالت ۱۲ رنگ با ترکیبی از رنگ‌های خاکی و شاین، مناسب آرایش روزانه و شب.',
                 specs={'رنگ': 'رنگارنگ', 'حجم': '۱۵ گرم', 'نوع': 'شاین و مات'}),
            dict(name='ریمل حجم‌دهنده ضدآب', category=makeup, brand='ولوت', sku='NK-003',
                 price=198000, compare_at_price=235000, stock=0, is_featured=False,
                 description='فرمول ضدآب که مژه‌ها را تا پایان روز حجیم و منحنی نگه می‌دارد.',
                 specs={'رنگ': 'مشکی', 'حجم': '۹ میل', 'نوع': 'ضدآب'}),
            dict(name='رژگونه هلویی سرامیک', category=makeup, brand='نیکا بیوتی', sku='NK-004',
                 price=225000, compare_at_price=None, stock=15, is_featured=False,
                 description='رژگونه‌ای با بافت نرم و پخش‌شوندگی عالی که درخشش طبیعی به گونه‌ها می‌دهد.',
                 specs={'رنگ': 'هلویی', 'حجم': '۶ گرم', 'نوع': 'پودری'}),
            dict(name='عطر گلرنگ بهاری ۵۰ میل', category=makeup, brand='اسنس', sku='NK-005',
                 price=690000, compare_at_price=820000, stock=5, is_featured=True,
                 description='رایحه‌ای گل‌محور با تلفیق یاس و پیونی، مناسب استفاده روزانه.',
                 specs={'حجم': '۵۰ میل', 'نوع': 'ادوپرفیوم'}),
            dict(name='براش آرایشی حرفه‌ای ست ۵ تایی', category=makeup, brand='لومیا', sku='NK-006',
                 price=320000, compare_at_price=None, stock=20, is_featured=False,
                 description='ست ۵ عددی براش با موی نرم مصنوعی برای اجرای بی‌نقص آرایش.',
                 specs={'رنگ': 'صورتی طلایی', 'نوع': 'ست'}),
            dict(name='رژ لب مایع میکاپ ماندگار', category=makeup, brand='ولوت', sku='NK-007',
                 price=245000, compare_at_price=270000, stock=9, is_featured=False,
                 description='فرمول سبک و ماندگار که تا ۸ ساعت روی لب باقی می‌ماند.',
                 specs={'رنگ': 'صورتی رزگلد', 'حجم': '۴ میل', 'نوع': 'مایع'}),
            dict(name='پالت سایه دودی اسموکی', category=makeup, brand='اسنس', sku='NK-008',
                 price=380000, compare_at_price=None, stock=3, is_featured=False,
                 description='رنگ‌های دودی برای طراحی چشم اسموکی حرفه‌ای.',
                 specs={'رنگ': 'دودی', 'حجم': '۱۲ گرم'}),
            dict(name='انگشتر نقره طرح برگ', category=accessory, brand='سیلورینو', sku='NK-009',
                 price=355000, compare_at_price=420000, stock=14, is_featured=True,
                 description='انگشتری ظریف با طرح برگ، ساخته‌شده از نقره استرلینگ ۹۲۵.',
                 specs={'رنگ': 'نقره‌ای', 'نوع': 'نقره ۹۲۵'}),
            dict(name='دستبند زنجیری استیل رزگلد', category=accessory, brand='گلدیرا', sku='NK-010',
                 price=290000, compare_at_price=None, stock=18, is_featured=True,
                 description='دستبند زنجیری با روکش رزگلد و استیل ضدحساسیت، مناسب پوست‌های حساس.',
                 specs={'رنگ': 'رزگلد', 'نوع': 'استیل ضدحساسیت'}),
            dict(name='گردنبند قلب مینیمال', category=accessory, brand='سیلورینو', sku='NK-011',
                 price=265000, compare_at_price=310000, stock=0, is_featured=False,
                 description='گردنبند مینیمال با پلاک قلب، مناسب استفاده روزمره.',
                 specs={'رنگ': 'طلایی', 'نوع': 'روکش طلا'}),
            dict(name='گوشواره مروارید کوچک', category=accessory, brand='گلدیرا', sku='NK-012',
                 price=210000, compare_at_price=None, stock=22, is_featured=False,
                 description='گوشواره میخی با نگین مروارید مصنوعی، سبک و ظریف.',
                 specs={'رنگ': 'سفید مروارید', 'نوع': 'میخی'}),
            dict(name='دستبند چرمی یونیسکس', category=accessory, brand='گلدیرا', sku='NK-013',
                 price=175000, compare_at_price=195000, stock=11, is_featured=False,
                 description='دستبند چرم طبیعی با قفل استیل، یونیسکس.',
                 specs={'رنگ': 'قهوه‌ای', 'نوع': 'چرم طبیعی'}),
            dict(name='عطر جیبی اسپرت', category=makeup, brand='اسنس', sku='NK-014',
                 price=150000, compare_at_price=None, stock=25, is_featured=False,
                 description='رایحه‌ای تازه و اسپرت، مناسب حمل در جیب و کیف.',
                 specs={'حجم': '۲۰ میل', 'نوع': 'ادوکلن'}),
        ]

        created_count = 0
        for p in products:
            obj, created = Product.objects.get_or_create(sku=p['sku'], defaults=p)
            if created:
                created_count += 1

        Coupon.objects.get_or_create(
            code='WELCOME10',
            defaults=dict(
                discount_type=Coupon.TYPE_PERCENT, value=10, min_amount=0,
                start_date=timezone.now() - timedelta(days=1),
                end_date=timezone.now() + timedelta(days=365),
                usage_limit=10000, is_active=True,
            )
        )

        Banner.objects.get_or_create(
            title='زیبایی تو، انتخاب تو',
            defaults=dict(subtitle='کالکشن جدید فصل رسید', order=1)
        )

        self.stdout.write(self.style.SUCCESS(
            f'✅ {created_count} محصول جدید، دسته‌بندی‌ها، کد تخفیف WELCOME10 و بنر نمونه ساخته شد.'
        ))
