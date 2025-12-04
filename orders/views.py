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
@permission_classes([IsAuthenticated])
def checkout(request):
    session_id = request.session.session_key or request.session.save()

    user_profile = None
    if request.user.is_authenticated:
        try:
            user_profile = request.user.userprofile
        except UserProfile.DoesNotExist:
            user_profile = None  # continue as guest

    # ----------------------------------------
    # 1️⃣ TRY: USER CART
    # ----------------------------------------
    cart = None
    if user_profile:
        cart = Cart.objects.filter(user=user_profile).first()

    if cart and cart.items.exists():
        items = cart.items.all()

    else:
        # ----------------------------------------
        # 2️⃣ TRY: SESSION CART (guest)
        # ----------------------------------------
        session_cart = Cart.objects.filter(session_id=session_id).first()

        if session_cart and session_cart.items.exists():
            items = session_cart.items.all()

        else:
            # ----------------------------------------
            # 3️⃣ FALLBACK: FRONTEND ITEMS
            # ----------------------------------------
            items_payload = request.data.get("items", [])
            if not items_payload:
                return Response(
                    {'error': 'Your cart is empty.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            from products.models import Product

            class TempItem:
                def __init__(self, product, quantity):
                    self.product = product
                    self.quantity = quantity

            items = []
            for i in items_payload:
                try:
                    product = Product.objects.get(id=i["product_id"])
                    items.append(TempItem(product, i["quantity"]))
                except Product.DoesNotExist:
                    continue

            if not items:
                return Response(
                    {'error': 'Your cart is empty.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

    # ----------------------------------------
    # 4️⃣ CALCULATE ORDER TOTAL
    # ----------------------------------------
    total_amount = sum(item.product.price * item.quantity for item in items)

    # ----------------------------------------
    # 5️⃣ CREATE ORDER
    # ----------------------------------------
    order = Order.objects.create(
        user=user_profile,            # null = guest
        session_id=session_id,        # save guest identifier
        total_amount=total_amount,
        address=request.data.get("address", "")
    )

    # ----------------------------------------
    # 6️⃣ CREATE ORDER ITEMS
    # ----------------------------------------
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

    # ----------------------------------------
    # 7️⃣ CLEAN UP CART
    # ----------------------------------------
    if cart:
        cart.items.all().delete()
    elif session_cart:
        session_cart.items.all().delete()

    serializer = OrderSerializer(order)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


# @api_view(["POST"])
# # @permission_classes([IsAuthenticated])
# def checkout(request):
#     try:
#         user_profile = request.user.userprofile
#     except UserProfile.DoesNotExist:
#         return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)
#
#     # Try to get user's cart
#     cart = Cart.objects.filter(user=user_profile).first()
#
#     if cart and cart.items.exists():
#         items = cart.items.all()
#     else:
#         # Fallback: use frontend payload
#         items_payload = request.data.get("items", [])
#         if not items_payload:
#             return Response({'error': 'Your cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)
#
#         # Build items dynamically without DB cart
#         class TempItem:
#             def __init__(self, product, quantity):
#                 self.product = product
#                 self.quantity = quantity
#
#         from products.models import Product  # adjust import
#         items = []
#         for i in items_payload:
#             try:
#                 product = Product.objects.get(id=i["product_id"])
#                 items.append(TempItem(product, i["quantity"]))
#             except Product.DoesNotExist:
#                 continue
#
#         if not items:
#             return Response({'error': 'Your cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)
#
#     # Calculate total
#     total_amount = sum(item.product.price * item.quantity for item in items)
#
#     # Create order
#     order = Order.objects.create(
#         user=user_profile,
#         total_amount=total_amount,
#         address=user_profile.address
#     )
#
#     # Create order items
#     order_items = [
#         OrderItem(
#             order=order,
#             product=item.product,
#             quantity=item.quantity,
#             price=item.product.price
#         )
#         for item in items
#     ]
#     OrderItem.objects.bulk_create(order_items)
#
#     # Clear cart if exists in DB
#     if cart:
#         cart.items.all().delete()
#
#     serializer = OrderSerializer(order)
#     return Response(serializer.data, status=status.HTTP_201_CREATED)

