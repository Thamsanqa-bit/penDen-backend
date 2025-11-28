from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import  Cart, CartItem
from products.models import Product
from cart.models import CartItem
from .serializers import CartSerializer
from accounts.models import UserProfile
from django.views.decorators.cache import cache_page
from rest_framework.pagination import PageNumberPagination

# Create your views here.
# @api_view(['GET'])
# def get_cart(request):
#     # Fetch cart and related data efficiently
#     cart = (
#         Cart.objects
#         .filter(user=request.user.userprofile)
#         .prefetch_related('items__product')
#         .first()
#     )
#
#     if not cart:
#         return Response({'items': [], 'total_price': 0})
#
#     # Get all cart items
#     items = cart.items.all().select_related('product')
#
#     # Apply pagination
#     paginator = PageNumberPagination()
#     paginator.page_size = 10
#     paginated_items = paginator.paginate_queryset(items, request)
#
#     # Serialize paginated items
#     serializer = CartItemSerializer(paginated_items, many=True)
#
#     # Return paginated response with total price
#     total_price = sum(item.product.price * item.quantity for item in items)
#
#     return paginator.get_paginated_response({
#         'items': serializer.data,
#         'total_price': total_price
#     })

@api_view(['GET'])
def get_cart(request):

    # Ensure session exists (required for guest users)
    if not request.session.session_key:
        request.session.create()
        request.session.save()

    # Determine correct cart
    if request.user.is_authenticated:
        try:
            user_profile = request.user.userprofile
            cart = Cart.objects.filter(user=user_profile).first()
        except:
            return Response({'items': [], 'total_price': 0})
    else:
        cart = Cart.objects.filter(session_key=request.session.session_key).first()

    if not cart:
        return Response({'items': [], 'total_price': 0})

    # Prefetch items
    items = cart.items.all().select_related('product')

    paginator = PageNumberPagination()
    paginator.page_size = 12
    paginated_items = paginator.paginate_queryset(items, request)

    serializer = CartItemSerializer(paginated_items, many=True)

    total_price = sum(item.product.price * item.quantity for item in items)

    return paginator.get_paginated_response({
        'items': serializer.data,
        'total_price': total_price
    })


@api_view(['POST'])
def add_to_cart(request):
    product_id = request.data.get('product_id')
    quantity = int(request.data.get('quantity', 1))

    if not product_id:
        return Response({'error': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

    # Ensure the session exists (for guest users)
    if not request.session.session_key:
        request.session.create()
        request.session.save()

    # If user is authenticated, use user-based cart
    if request.user.is_authenticated:
        try:
            # Get the UserProfile instance instead of User
            user_profile = request.user.userprofile
            cart, _ = Cart.objects.get_or_create(user=user_profile)
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)
    else:
        # Guest cart tied to session key
        cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key)

    # Get or create the cart item
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if created:
        cart_item.quantity = quantity
    else:
        cart_item.quantity += quantity

    cart_item.save()

    serializer = CartSerializer(cart)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def remove_from_cart(request):
    print(f"DEBUG: User: {request.user}, Authenticated: {request.user.is_authenticated}")
    print(f"DEBUG: Product ID: {request.data.get('product_id')}")
    print(f"DEBUG: Initial Session Key: {request.session.session_key}")

    product_id = request.data.get('product_id')

    try:
        quantity = int(request.data.get('quantity', 1))
    except (TypeError, ValueError):
        return Response({'error': 'Invalid quantity'}, status=status.HTTP_400_BAD_REQUEST)

    if not product_id:
        return Response({'error': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)

    # FIXED: Proper session handling for guest users
    if not request.user.is_authenticated:
        if not request.session.session_key:
            request.session.create()
            request.session.save()  # This is crucial - saves the session to database
            print(f"DEBUG: Created new session key: {request.session.session_key}")
        else:
            print(f"DEBUG: Using existing session key: {request.session.session_key}")

    # Identify which cart to use
    if request.user.is_authenticated:
        try:
            # Get the UserProfile instance instead of User
            user_profile = request.user.userprofile
            cart, created = Cart.objects.get_or_create(user=user_profile)
            if created:
                print(f"DEBUG: Created new cart for authenticated user")
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)
    else:
        # FIXED: Use get_or_create for guest cart with proper session key
        if not request.session.session_key:
            return Response({'error': 'Session not available'}, status=status.HTTP_400_BAD_REQUEST)

        cart, created = Cart.objects.get_or_create(session_key=request.session.session_key)
        if created:
            print(f"DEBUG: Created new cart for session: {request.session.session_key}")

    print(f"DEBUG: Cart ID: {cart.id}")

    # Try to find the product
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

    cart_items = CartItem.objects.filter(cart=cart)
    print(f"DEBUG: Cart has {cart_items.count()} items")
    print(f"DEBUG: Cart items: {list(cart_items.values_list('product_id', flat=True))}")

    # Find the cart item - using filter().first() for better handling
    cart_item = CartItem.objects.filter(cart=cart, product=product).first()

    if not cart_item:
        return Response({
            'error': 'Item not found in cart',
            'debug_info': {
                'cart_id': cart.id,
                'product_id': product_id,
                'cart_items_count': cart_items.count(),
                'existing_product_ids': list(cart_items.values_list('product_id', flat=True)),
                'session_key': request.session.session_key,
                'user_authenticated': request.user.is_authenticated
            }
        }, status=status.HTTP_404_NOT_FOUND)

    # Reduce or remove quantity
    if cart_item.quantity > quantity:
        cart_item.quantity -= quantity
        cart_item.save()
        print(f"DEBUG: Reduced quantity to {cart_item.quantity}")
    else:
        cart_item.delete()
        print(f"DEBUG: Removed item completely from cart")

    # Return updated cart
    serializer = CartSerializer(cart)
    return Response(serializer.data, status=status.HTTP_200_OK)
# @api_view(['POST'])
# def remove_from_cart(request):
#     print(f"DEBUG: User: {request.user}, Authenticated: {request.user.is_authenticated}")
#     print(f"DEBUG: Product ID: {request.data.get('product_id')}")
#
#     product_id = request.data.get('product_id')
#     quantity = int(request.data.get('quantity', 1))
#
#     if not product_id:
#         return Response({'error': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)
#
#     # Ensure session exists for guest users
#     if not request.session.session_key:
#         request.session.create()
#         request.session.save()
#         print(f"DEBUG: Created new session key: {request.session.session_key}")
#     # Identify which cart to use
#     if request.user.is_authenticated:
#         try:
#             # Get the UserProfile instance instead of User
#             user_profile = request.user.userprofile
#             cart = Cart.objects.filter(user=user_profile).first()
#         except UserProfile.DoesNotExist:
#             return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)
#     else:
#         cart = Cart.objects.filter(session_key=request.session.session_key).first()
#
#     if not cart:
#         return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
#
#     # Try to find the product
#     try:
#         product = Product.objects.get(id=product_id)
#     except Product.DoesNotExist:
#         return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
#
#     cart_items = CartItem.objects.filter(cart=cart)
#     print(f"DEBUG: Cart has {cart_items.count()} items")
#     print(f"DEBUG: Cart items: {list(cart_items.values_list('product_id', flat=True))}")
#
#     # Find the cart item
#     try:
#         cart_item = CartItem.objects.get(cart=cart, product=product)
#     except CartItem.DoesNotExist:
#         return Response({'error': 'Item not found in cart'}, status=status.HTTP_404_NOT_FOUND)
#
#     # Reduce or remove quantity
#     if cart_item.quantity > quantity:
#         cart_item.quantity -= quantity
#         cart_item.save()
#     else:
#         cart_item.delete()
#
#     # Return updated cart
#     serializer = CartSerializer(cart)
#     return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['PUT'])
def update_cart(request):
    product_id = request.data.get('product_id')
    quantity = request.data.get('quantity')

    #Validate inputs
    if not product_id or quantity is None:
        return Response({'error': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        quantity = int(quantity)
        if quantity < 0:
            return Response({'error': 'Quantity must be non-negative'}, status=status.HTTP_400_BAD_REQUEST)
    except ValueError:
        return Response({'error': 'Quantity must be a number'}, status=status.HTTP_400_BAD_REQUEST)

    # Ensure session exists (for guest carts)
    if not request.session.session_key:
        request.session.create()
        request.session.save()

    # Get correct cart depending on auth
    user_profile = request.user.userprofile
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=user_profile).first()
    else:
        cart = Cart.objects.filter(session_key=request.session.session_key, user=None).first()

    if not cart:
        return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)

    #Get product and item
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

    try:
        cart_item = CartItem.objects.get(cart=cart, product=product)
    except CartItem.DoesNotExist:
        return Response({'error': 'Item not found in cart'}, status=status.HTTP_404_NOT_FOUND)

    # Update quantity or remove if zero
    if quantity == 0:
        cart_item.delete()
    else:
        cart_item.quantity = quantity
        cart_item.save()

    serializer = CartSerializer(cart)
    return Response(serializer.data, status=status.HTTP_200_OK)
