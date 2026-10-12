from django.urls import path

from .views import StartPaymentView, VerifyPaymentView

urlpatterns = [
    path('payments/start/', StartPaymentView.as_view(), name='payment-start'),
    path('payments/verify/', VerifyPaymentView.as_view(), name='payment-verify'),
]
