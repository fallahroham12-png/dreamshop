"""
اتصال به درگاه پرداخت زرین‌پال.

نکته مهم امنیتی (بخش ۱۱ و ۲۲ سند نیازمندی):
هرگز نباید فقط بر اساس بازگشت کاربر از درگاه، پرداخت را موفق در نظر گرفت.
تابع verify_payment باید همیشه با فراخوانی واقعی API درگاه، صحت تراکنش را
تأیید کند و فقط در صورت پاسخ موفق از سمت درگاه، سفارش را «پرداخت‌شده» علامت بزند.

این فایل یک Wrapper ساده و قابل جایگزینی است — در صورت تغییر درگاه (مثلاً به
آیدی‌پی یا پی‌پینگ)، فقط کافیست همین یک فایل بازنویسی شود.
"""
import requests
from django.conf import settings


class ZarinpalGateway:
    SANDBOX_BASE = 'https://sandbox.zarinpal.com/pg/v4/payment'
    PRODUCTION_BASE = 'https://api.zarinpal.com/pg/v4/payment'
    SANDBOX_STARTPAY = 'https://sandbox.zarinpal.com/pg/StartPay/'
    PRODUCTION_STARTPAY = 'https://www.zarinpal.com/pg/StartPay/'

    def __init__(self):
        self.merchant_id = settings.ZARINPAL_MERCHANT_ID
        self.sandbox = settings.ZARINPAL_SANDBOX
        self.base_url = self.SANDBOX_BASE if self.sandbox else self.PRODUCTION_BASE
        self.startpay_url = self.SANDBOX_STARTPAY if self.sandbox else self.PRODUCTION_STARTPAY

    def request_payment(self, *, amount_rial: int, description: str, mobile: str = '', callback_url: str = None):
        """
        مرحله اول پرداخت — گرفتن Authority از درگاه.
        خروجی: (success: bool, authority_or_error: str, payment_url: str|None)
        """
        payload = {
            'merchant_id': self.merchant_id,
            'amount': amount_rial,
            'description': description,
            'callback_url': callback_url or settings.ZARINPAL_CALLBACK_URL,
            'metadata': {'mobile': mobile} if mobile else {},
        }
        try:
            resp = requests.post(f'{self.base_url}/request.json', json=payload, timeout=10)
            data = resp.json()
        except requests.RequestException as exc:
            return False, str(exc), None

        if data.get('data', {}).get('code') == 100:
            authority = data['data']['authority']
            return True, authority, f'{self.startpay_url}{authority}'
        error_msg = data.get('errors', {}).get('message', 'خطای نامشخص از درگاه پرداخت')
        return False, error_msg, None

    def verify_payment(self, *, amount_rial: int, authority: str):
        """
        مرحله دوم — تأیید واقعی تراکنش بعد از بازگشت کاربر از درگاه.
        این فراخوانی است که واقعاً مشخص می‌کند پرداخت موفق بوده یا نه؛
        هرگز نباید این مرحله حذف یا دور زده شود.
        خروجی: (success: bool, ref_id_or_error: str, raw_response: dict)
        """
        payload = {
            'merchant_id': self.merchant_id,
            'amount': amount_rial,
            'authority': authority,
        }
        try:
            resp = requests.post(f'{self.base_url}/verify.json', json=payload, timeout=10)
            data = resp.json()
        except requests.RequestException as exc:
            return False, str(exc), {}

        result_code = data.get('data', {}).get('code')
        if result_code in (100, 101):  # 101 یعنی قبلاً تأیید شده (idempotent)
            ref_id = data['data'].get('ref_id', '')
            return True, ref_id, data
        error_msg = data.get('errors', {}).get('message', 'تأیید پرداخت ناموفق بود.')
        return False, error_msg, data


def get_gateway():
    """در آینده اگر درگاه دیگری اضافه شد، انتخاب درگاه می‌تواند اینجا بر اساس تنظیمات انجام شود."""
    return ZarinpalGateway()
