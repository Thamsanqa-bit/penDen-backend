from django.urls import path
from .views import create_payment, payfast_notify

urlpatterns = [
    path('api/create-payment/', create_payment, name='create-payment'),
    path('api/payment/notify/', payfast_notify, name='payfast_notify'),
]