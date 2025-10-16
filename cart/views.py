from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import  Cart, CartItem
from products.models import Product
from cart.models import CartItem
from .serializers import CartSerializer

# Create your views here.
@api_view(['GET'])
def get_cart(request):
    cart = Cart.objects.filter(user=request.user).first()
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

    #Use get_or_create instead of always creating a new cart
    cart, _ = Cart.objects.get_or_create(user_id=1)

    #Get or create the cart item
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if created:
        cart_item.quantity = quantity
    else:
        #Increase existing quantity
        cart_item.quantity += quantity

    cart_item.save()

    serializer = CartSerializer(cart)
    return Response(serializer.data, status=status.HTTP_200_OK)

# @api_view(['POST'])
# def add_to_cart(request):
#     product_id = request.data.get('product_id')
#     quantity = int(request.data.get('quantity', 1))
#
#     if not product_id:
#         return Response({'error': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)
#
#     try:
#         product = Product.objects.get(id=product_id)
#     except Product.DoesNotExist:
#         return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
#
#     # cart= Cart.objects.create(user=request.user)
#     # cart = Cart.objects.create(user_id=1)
#     cart, _ = Cart.objects.get_or_create(user_id=1)
#     cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
#
#     if not created:
#         # cart_item.quantity = quantity
#         cart_item.quantity += quantity
#         cart_item.save()
#
#     serializer = CartSerializer(cart)
#     return Response(serializer.data, status=200)


@api_view(['POST'])
def remove_from_cart(request):
    product_id = request.data.get('product_id')
    quantity = int(request.data.get('quantity', 1))

    if not product_id:
        return Response({'error': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)

    # In your real app, use `request.user`
    cart = Cart.objects.filter(user_id=1).first()

    if not cart:
        return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

    try:
        cart_item = CartItem.objects.get(cart=cart, product=product)
    except CartItem.DoesNotExist:
        return Response({'error': 'Item not found in cart'}, status=status.HTTP_404_NOT_FOUND)

    # Reduce quantity
    if cart_item.quantity > quantity:
        cart_item.quantity -= quantity
        cart_item.save()
    else:
        # Remove item if quantity goes to 0 or less
        cart_item.delete()

    # Recalculate cart totals (if your model tracks total amount)
    serializer = CartSerializer(cart)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def update_cart(request):
    pass