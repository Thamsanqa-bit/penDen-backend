from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import  Cart, CartItem
from products.models import Product
from cart.models import CartItem
from .serializers import CartSerializer
from accounts.models import UserProfile
from django.views.decorators.cache import cache_page

#@cache_page(60 * 15)  # cache for 15 minutes
# Create your views here.
@api_view(['GET'])
def get_cart(request):
    cart = Cart.objects.filter(user=request.user.userprofile).first()
    if not cart:
        return Response({'items': [], 'total_price': 0})
    serializer = CartSerializer(cart)
    return Response(serializer.data)

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
    product_id = request.data.get('product_id')
    quantity = int(request.data.get('quantity', 1))

    if not product_id:
        return Response({'error': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)

    # Ensure session exists for guest users
    if not request.session.session_key:
        request.session.create()

    # Identify which cart to use
    if request.user.is_authenticated:
        try:
            # Get the UserProfile instance instead of User
            user_profile = request.user.userprofile
            cart = Cart.objects.filter(user=user_profile).first()
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)
    else:
        cart = Cart.objects.filter(session_key=request.session.session_key).first()

    if not cart:
        return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)

    # Try to find the product
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

    # Find the cart item
    try:
        cart_item = CartItem.objects.get(cart=cart, product=product)
    except CartItem.DoesNotExist:
        return Response({'error': 'Item not found in cart'}, status=status.HTTP_404_NOT_FOUND)

    # Reduce or remove quantity
    if cart_item.quantity > quantity:
        cart_item.quantity -= quantity
        cart_item.save()
    else:
        cart_item.delete()

    # Return updated cart
    serializer = CartSerializer(cart)
    return Response(serializer.data, status=status.HTTP_200_OK)

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
