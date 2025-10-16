from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Order, OrderItem
from products.models import Product  # adjust path if needed
from .serializers import OrderSerializer

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def checkout(request):
    cart = request.data.get("cart", {})

    if not cart or not isinstance(cart, dict):
        return Response({"error": "Invalid or empty cart."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        total_amount = 0
        order = Order.objects.create(user=request.user)

        for product_id, quantity in cart.items():
            product = Product.objects.get(id=product_id)
            subtotal = product.price * quantity
            total_amount += subtotal

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                subtotal=subtotal
            )

        order.total_amount = total_amount
        order.save()

        serializer = OrderSerializer(order)
        return Response({"message": "Order placed successfully!", "order": serializer.data}, status=status.HTTP_201_CREATED)

    except Product.DoesNotExist:
        return Response({"error": "One or more products not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print("Checkout error:", str(e))
        return Response({"error": "Something went wrong during checkout."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# from django.shortcuts import render
# from .serializers import OrderSerializer
# from rest_framework.response import Response
# from rest_framework.decorators import api_view
# from products.models import Product
# from accounts.models import UserProfile
# from cart.models import CartItem
# from orders.models import Order
# from rest_framework.permissions import IsAuthenticated
# from rest_framework import status  # Import status module
#
# # Create your views here.
# @api_view(['POST'])
# # @permission_classes([IsAuthenticated])
# def checkout(request):
#     # user = request.user
#     user_id = 1
#     try:
#         profile = UserProfile.objects.get(user_id=user_id)
#     except UserProfile.DoesNotExist:
#         return Response({'error': 'User profile not found. Please create a profile.'}, status=status.HTTP_400_BAD_REQUEST)
#
#     cart_item = CartItem.objects.filter(cart_id=user_id)
#     if not cart_item.exists():
#         return Response({'error': 'User cart item not found.'}, status=status.HTTP_400_BAD_REQUEST)
#
#     order = Order.objects.create(user_profile_id=user_id,
#                                  address=profile.address,
#                                  total_amount=sum(item.product.price * item.quantity for item in cart_items)
#                                  )
#     # Add items to the order
#     for item in cart_items:
#         OrderItem.objects.create(
#             order=order,
#             product=item.product,
#             quantity=item.quantity,
#             price=item.product.price
#         )
#
#     # Clear the cart
#     cart_items.delete()
#
#     return Response({
#         'message': 'Order created successfully',
#         'order_id': order.id,
#         'total_amount': order.total_amount
#     }, status=status.HTTP_201_CREATED)