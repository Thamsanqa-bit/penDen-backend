import hashlib
from rest_framework.decorators import api_view
from urllib.parse import urlencode
from django.http import JsonResponse
from django.conf import settings
from orders.models import Order

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
import json


@csrf_exempt
@api_view(["POST"])
def create_payment(request):
    # Simple test version
    try:
        print("=== DEBUG: create_payment called ===")

        # Check request data
        print(f"Request data: {request.data}")

        # Test with hardcoded values to isolate the issue
        test_data = {
            "merchant_id": "19466755",
            "merchant_key": "bbn1mlrvljzu1",
            "amount": "100.00",
            "item_name": "Test Order Payment",
            "return_url": "https://penden.online/payment/success",
            "cancel_url": "https://penden.online/payment/cancel",
            "notify_url": "https://penden.online/api/payment/notify/",
        }

        payment_url = "https://www.payfast.co.za/eng/process?" + urlencode(test_data)
        print(f"Generated URL: {payment_url}")

        return Response({
            "payment_url": payment_url,
            "debug": "Test mode - using hardcoded values"
        })

    except Exception as e:
        print(f"=== ERROR: {str(e)} ===")
        import traceback
        traceback.print_exc()
        return Response({"error": str(e)}, status=500)
#
# @csrf_exempt
# @api_view(["POST"])
# def create_payment(request):
#     amount = request.GET.get("amount")
#
#     data = {
#         "merchant_id": settings.PAYFAST_MERCHANT_ID,
#         "merchant_key": settings.PAYFAST_MERCHANT_KEY,
#         "amount": amount,
#         "item_name": "Order Payment",
#         "return_url": settings.PAYFAST_RETURN_URL,
#         "cancel_url": settings.PAYFAST_CANCEL_URL,
#         "notify_url": settings.PAYFAST_NOTIFY_URL,
#     }
#
#     # Generate payment URL
#     payment_url = "https://www.payfast.co.za/eng/process?" + urlencode(data)
#     return JsonResponse({"payment_url": payment_url})


@csrf_exempt
def payfast_notify(request):
    # PayFast sends POST with payment details
    data = request.POST

    # You would verify hash + save transaction
    print("PayFast payment received:", data)

    return HttpResponse("OK", status=200)

