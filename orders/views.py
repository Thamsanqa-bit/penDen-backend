from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Order, OrderItem
from products.models import Product
from .serializers import OrderSerializer
from cart.models import Cart, UserProfile
from django.views.decorators.cache import cache_page

@api_view(["POST"])
# @permission_classes([IsAuthenticated])
def checkout(request):
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)

    # Try to get user's cart
    cart = Cart.objects.filter(user=user_profile).first()

    if cart and cart.items.exists():
        items = cart.items.all()
    else:
        # Fallback: use frontend payload
        items_payload = request.data.get("items", [])
        if not items_payload:
            return Response({'error': 'Your cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)

        # Build items dynamically without DB cart
        class TempItem:
            def __init__(self, product, quantity):
                self.product = product
                self.quantity = quantity

        from products.models import Product  # adjust import
        items = []
        for i in items_payload:
            try:
                product = Product.objects.get(id=i["product_id"])
                items.append(TempItem(product, i["quantity"]))
            except Product.DoesNotExist:
                continue

        if not items:
            return Response({'error': 'Your cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)

    # Calculate total
    total_amount = sum(item.product.price * item.quantity for item in items)

    # Create order
    order = Order.objects.create(
        user=user_profile,
        total_amount=total_amount,
        address=user_profile.address
    )

    # Create order items
    order_items = [
        OrderItem(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price
        )
        for item in items
    ]
    OrderItem.objects.bulk_create(order_items)

    # Clear cart if exists in DB
    if cart:
        cart.items.all().delete()

    serializer = OrderSerializer(order)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

# @api_view(["POST"])
# @permission_classes([IsAuthenticated])
# def checkout(request):
#     user = request.user.userprofile
#     address = request.data.get('address', '')
#
#     cart = Cart.objects.filter(user=user).first()
#     if not cart or not cart.items.exists():
#         return Response({'error': 'Your cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)
#
#     # Calculate total
#     total_amount = sum(item.product.price * item.quantity for item in cart.items.all())
#
#     # Create order
#     order = Order.objects.create(
#         user=user,
#         total_amount=total_amount,
#         address=address
#     )
#
#     # Create order items
#     for item in cart.items.all():
#         OrderItem.objects.create(
#             order=order,
#             product=item.product,
#             quantity=item.quantity,
#             price=item.product.price
#         )
#
#     # Clear cart
#     cart.items.all().delete()
#
#     serializer = OrderSerializer(order)
#     return Response(serializer.data, status=status.HTTP_201_CREATED)

# def checkout(request):
#     cart = request.data.get("cart", {})
#
#     if not cart or not isinstance(cart, dict):
#         return Response({"error": "Invalid or empty cart."}, status=status.HTTP_400_BAD_REQUEST)
#
#     try:
#         total_amount = 0
#         order = Order.objects.create(user=request.user)
#
#         for product_id, quantity in cart.items():
#             product = Product.objects.get(id=product_id)
#             subtotal = product.price * quantity
#             total_amount += subtotal
#
#             OrderItem.objects.create(
#                 order=order,
#                 product=product,
#                 quantity=quantity,
#                 subtotal=subtotal
#             )
#
#         order.total_amount = total_amount
#         order.save()
#
#         serializer = OrderSerializer(order)
#         return Response({"message": "Order placed successfully!", "order": serializer.data}, status=status.HTTP_201_CREATED)
#
#     except Product.DoesNotExist:
#         return Response({"error": "One or more products not found."}, status=status.HTTP_404_NOT_FOUND)
#     except Exception as e:
#         print("Checkout error:", str(e))
#         return Response({"error": "Something went wrong during checkout."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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