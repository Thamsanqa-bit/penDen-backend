from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from urllib.parse import urlencode
from orders.models import Order
import os
from django.conf import settings

@api_view(['GET'])

@csrf_exempt
@api_view(["POST"])
def create_payment(request):
    try:
        print("=== DEBUG: create_payment called ===")
        print("Request data:", request.data)

        order_id = request.data.get("order_id")
        amount = request.data.get("amount")  # amount from frontend

        if not order_id or not amount:
            return Response(
                {"error": "order_id and amount are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate order exists
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)

        # Convert amount safely
        try:
            amount = float(amount)
        except:
            return Response({"error": "Invalid amount format"}, status=400)

        # Format to 2 decimals for PayFast
        amount_str = f"{amount:.2f}"

        print(f"Valid amount received: {amount_str}")

        # PayFast required fields
        data = {
            "merchant_id": "19466755",
            "merchant_key": "bbn1mlrvljzu1",
            "return_url": "https://penden.online/payment/success",
            "cancel_url": "https://penden.online/payment/cancel",
            "notify_url": "https://penden.online/api/payment/notify/",
            "amount": amount_str,
            "item_name": f"Order #{order_id}",
        }

        # Generate PayFast process URL
        payment_url = "https://www.payfast.co.za/eng/process?" + urlencode(data)

        print("Generated PayFast URL:", payment_url)

        return Response({"payment_url": payment_url})

    except Exception as e:
        print("=== ERROR in create_payment ===", str(e))
        return Response({"error": str(e)}, status=500)



@csrf_exempt
def payfast_notify(request):
    # PayFast sends POST with payment details
    data = request.POST

    # You would verify hash + save transaction
    print("PayFast payment received:", data)

    return HttpResponse("OK", status=200)

