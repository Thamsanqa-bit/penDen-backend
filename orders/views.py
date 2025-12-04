# views.py - Updated checkout view
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Order, OrderItem
from products.models import Product
from .serializers import OrderSerializer
from cart.models import Cart, UserProfile


@api_view(["POST"])
def checkout(request):
    """
    Handle checkout for both logged-in and guest users
    Expects: {
        "items": [{"product_id": 1, "quantity": 2}, ...],
        "address": "Shipping address"
    }
    """
    session_id = request.session.session_key or request.session.save()

    # Get user profile if user is authenticated
    user_profile = None
    if request.user.is_authenticated:
        try:
            user_profile = request.user.userprofile
        except UserProfile.DoesNotExist:
            user_profile = None

    # Get items from payload
    items_payload = request.data.get("items", [])
    address = request.data.get("address", "")

    if not items_payload:
        return Response(
            {'error': 'Your cart is empty.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Validate required address
    if not address:
        return Response(
            {'error': 'Shipping address is required.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Build items list
    class TempItem:
        def __init__(self, product, quantity):
            self.product = product
            self.quantity = quantity

    items = []
    total_amount = 0

    for item_data in items_payload:
        try:
            product_id = item_data.get("product_id")
            quantity = int(item_data.get("quantity", 1))

            if quantity <= 0:
                continue

            product = Product.objects.get(id=product_id)
            items.append(TempItem(product, quantity))
            total_amount += product.price * quantity

        except (Product.DoesNotExist, ValueError, TypeError) as e:
            print(f"Error processing item: {e}")
            continue

    if not items:
        return Response(
            {'error': 'No valid items in cart.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Create order
    order = Order.objects.create(
        user=user_profile,  # Will be None for guest users
        session_id=session_id if not user_profile else None,  # Store session ID for guests
        total_amount=total_amount,
        address=address,
        status="pending"
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

    # Clear user's cart if exists
    if user_profile:
        Cart.objects.filter(user=user_profile).delete()

    # Clear session cart if exists
    Cart.objects.filter(session_id=session_id).delete()

    serializer = OrderSerializer(order)
    return Response(serializer.data, status=status.HTTP_201_CREATED)