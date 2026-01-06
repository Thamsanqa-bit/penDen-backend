from django.urls import path
from .views import create_payment, payfast_notify

urlpatterns = [
    path('create-payment/', create_payment, name='create-payment'),
    path('payment/notify/', payfast_notify, name='payfast_notify'),
]