from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import  Cart, CartItem
from products.models import Product
from .serializers import CartSerializer

# Create your views here.
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

    # cart= Cart.objects.create(user=request.user)
    cart = Cart.objects.create(user_id=1)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        cart_item.quantity = quantity
        cart_item.save()

    serializer = CartSerializer(cart)
    return Response(serializer.data, status=200)

@api_view(['GET'])
def get_cart(request):
    cart = Cart.objects.filter(user=request.user).first()
    if not cart:
        return Response({'items': [], 'total_price': 0})
    serializer = CartSerializer(cart)
    return Response(serializer.data)

