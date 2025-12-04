import hashlib
from rest_framework.decorators import api_view
from urllib.parse import urlencode
from django.http import JsonResponse
from django.conf import settings

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse


def create_payment(request):
    amount = request.GET.get("amount")

    data = {
        "merchant_id": settings.PAYFAST_MERCHANT_ID,
        "merchant_key": settings.PAYFAST_MERCHANT_KEY,
        "amount": amount,
        "item_name": "Order Payment",
        "return_url": settings.PAYFAST_RETURN_URL,
        "cancel_url": settings.PAYFAST_CANCEL_URL,
        "notify_url": settings.PAYFAST_NOTIFY_URL,
    }

    # Generate payment URL
    payment_url = "https://www.payfast.co.za/eng/process?" + urlencode(data)
    return JsonResponse({"payment_url": payment_url})


@csrf_exempt
def payfast_notify(request):
    # PayFast sends POST with payment details
    data = request.POST

    # You would verify hash + save transaction
    print("PayFast payment received:", data)

    return HttpResponse("OK", status=200)

