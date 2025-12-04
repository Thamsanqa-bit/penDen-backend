import hashlib
from rest_framework.decorators import api_view
from urllib.parse import urlencode
from django.http import JsonResponse
from django.conf import settings

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
import json


@csrf_exempt
@api_view(["POST"])
def create_payment(request):
    try:
        # Parse JSON data from POST request
        if isinstance(request.data, str):
            data = json.loads(request.data)
        else:
            data = request.data

        order_id = data.get("order_id")

        if not order_id:
            return Response({"error": "Order ID is required"}, status=400)

        try:
            order = Order.objects.get(id=order_id)

            # Validate amount
            if order.total_amount is None or order.total_amount <= 0:
                return Response({"error": "Invalid order amount"}, status=400)

            # Format amount to 2 decimal places
            amount = "{:.2f}".format(order.total_amount)

            payfast_data = {
                "merchant_id": settings.PAYFAST_MERCHANT_ID,
                "merchant_key": settings.PAYFAST_MERCHANT_KEY,
                "amount": amount,
                "item_name": f"Order #{order.id} Payment",
                "return_url": settings.PAYFAST_RETURN_URL,
                "cancel_url": settings.PAYFAST_CANCEL_URL,
                "notify_url": settings.PAYFAST_NOTIFY_URL,
            }

            payment_url = "https://www.payfast.co.za/eng/process?" + urlencode(payfast_data)
            return Response({"payment_url": payment_url})

        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)

    except Exception as e:
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

