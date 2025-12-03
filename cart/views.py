from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Cart, CartItem
from products.models import Product
from .serializers import CartSerializer
from accounts.models import UserProfile
from django.db import transaction


@api_view(['GET'])
def get_cart(request):
    """
    Get cart for current user (authenticated or guest)
    """
    # Ensure session exists
    if not request.session.session_key:
        request.session.create()
    request.session.save()

    session_key = request.session.session_key

    try:
        if request.user.is_authenticated:
            try:
                user_profile = request.user.userprofile
                cart, created = Cart.objects.get_or_create(user=user_profile)
            except UserProfile.DoesNotExist:
                return Response({
                    'items': [],
                    'total_price': 0,
                    'total_items': 0
                }, status=status.HTTP_200_OK)
        else:
            cart, created = Cart.objects.get_or_create(session_key=session_key)

        # Use serializer which handles image serialization properly
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        print(f"ERROR in get_cart: {str(e)}")
        return Response({
            'items': [],
            'total_price': 0,
            'total_items': 0,
            'error': str(e)
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
def add_to_cart(request):
    """
    Add item to cart - FIXED version that properly increments
    """
    product_id = request.data.get('product_id')
    quantity = int(request.data.get('quantity', 1))

    print(f"DEBUG add_to_cart STARTED")
    print(f"Product ID: {product_id}, Quantity: {quantity}")
    print(f"User: {request.user}, Authenticated: {request.user.is_authenticated}")
    print(f"Session Key: {request.session.session_key}")

    if not product_id:
        return Response({'error': 'Product ID is required'}, status=status.HTTP_400_BAD_REQUEST)

    if quantity < 1:
        return Response({'error': 'Quantity must be at least 1'}, status=status.HTTP_400_BAD_REQUEST)

    # Ensure session exists
    if not request.session.session_key:
        print("Creating new session...")
        request.session.create()
    request.session.save()

    session_key = request.session.session_key
    print(f"Using session_key: {session_key}")

    try:
        product = Product.objects.get(id=product_id)
        print(f"Found product: {product.name} (ID: {product.id})")
    except Product.DoesNotExist:
        print(f"Product not found: {product_id}")
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

    try:
        # Get or create cart
        if request.user.is_authenticated:
            try:
                user_profile = request.user.userprofile
                cart, cart_created = Cart.objects.get_or_create(user=user_profile)
                print(f"🛒 User cart: {'CREATED' if cart_created else 'EXISTS'} (ID: {cart.id})")
            except UserProfile.DoesNotExist:
                print(f"User profile not found for user: {request.user}")
                return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            cart, cart_created = Cart.objects.get_or_create(session_key=session_key)
            print(f"🛒 Guest cart: {'CREATED' if cart_created else 'EXISTS'} (ID: {cart.id})")

        # DEBUG: Print all items in cart before operation
        print(f"Checking all items in cart ID {cart.id}:")
        for item in cart.items.all():
            print(f"   - Product ID: {item.product.id}, Quantity: {item.quantity}")

        # Use get_or_create with update
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )

        if not created:
            # Item already exists - INCREMENT
            print(f"Item already exists! Current quantity: {cart_item.quantity}")

            # FIXED: Use regular increment instead of F() expression
            cart_item.quantity += quantity
            cart_item.save()

            print(f"Incremented by {quantity}. New quantity: {cart_item.quantity}")
            action = "incremented"
        else:
            # New item created
            print(f"Created new item with quantity: {cart_item.quantity}")
            action = "added"

        # FIXED: Refresh from database to get the actual value
        cart_item.refresh_from_db()
        print(f"Final check - Product ID: {cart_item.product.id}, Final Quantity: {cart_item.quantity}")

        # Refresh the entire cart
        cart.refresh_from_db()

        # Use serializer
        serializer = CartSerializer(cart)
        response_data = serializer.data
        response_data['message'] = f'Product {action} to cart successfully'
        response_data['action'] = action
        response_data['new_quantity'] = cart_item.quantity

        print(f"SUCCESS: Item {action}. New quantity: {cart_item.quantity}")
        print(f"Cart total items: {response_data.get('total_items', 0)}")

        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        print(f"ERROR in add_to_cart: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({'error': f'Failed to add item to cart: {str(e)}'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def update_cart_item(request):
    """
    Update item quantity in cart - set specific quantity
    """
    product_id = request.data.get('product_id')
    quantity = request.data.get('quantity')

    print(f"DEBUG update_cart_item STARTED")
    print(f"Product ID: {product_id}, New Quantity: {quantity}")
    print(f"User: {request.user}, Authenticated: {request.user.is_authenticated}")

    if not product_id:
        return Response({'error': 'Product ID is required'}, status=status.HTTP_400_BAD_REQUEST)

    if quantity is None:
        return Response({'error': 'Quantity is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        quantity = int(quantity)
        if quantity < 0:
            return Response({'error': 'Quantity cannot be negative'}, status=status.HTTP_400_BAD_REQUEST)
    except (ValueError, TypeError):
        return Response({'error': 'Quantity must be a valid number'}, status=status.HTTP_400_BAD_REQUEST)

    # Ensure session exists
    if not request.session.session_key:
        request.session.create()
    request.session.save()

    session_key = request.session.session_key
    print(f"Using session_key: {session_key}")

    try:
        product = Product.objects.get(id=product_id)
        print(f"Found product: {product.name} (ID: {product.id})")
    except Product.DoesNotExist:
        print(f"Product not found: {product_id}")
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

    try:
        # Get or create cart
        if request.user.is_authenticated:
            try:
                user_profile = request.user.userprofile
                cart, cart_created = Cart.objects.get_or_create(user=user_profile)
                print(f"🛒 User cart: {'CREATED' if cart_created else 'EXISTS'} (ID: {cart.id})")
            except UserProfile.DoesNotExist:
                print(f"User profile not found for user: {request.user}")
                return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            cart, cart_created = Cart.objects.get_or_create(session_key=session_key)
            print(f"Guest cart: {'CREATED' if cart_created else 'EXISTS'} (ID: {cart.id})")

        # DEBUG: Print all items in cart before operation
        print(f"Checking all items in cart ID {cart.id} before update:")
        for item in cart.items.all():
            print(f"   - Product ID: {item.product.id}, Quantity: {item.quantity}")

        # Find cart item
        cart_item = CartItem.objects.filter(cart=cart, product=product).first()

        if quantity == 0:
            # If quantity is 0, remove the item
            if cart_item:
                cart_item.delete()
                message = 'Item removed from cart'
                action = 'removed'
                print(f"Item removed (quantity set to 0)")
            else:
                # Item doesn't exist in cart
                message = 'Item not in cart'
                action = 'no_change'
                print(f"ℹItem not in cart, no action needed")
        else:
            # Update or create item with new quantity
            if cart_item:
                # Update existing item
                old_quantity = cart_item.quantity
                cart_item.quantity = quantity
                cart_item.save()
                message = f'Quantity updated from {old_quantity} to {quantity}'
                action = 'updated'
                print(f"Updated quantity from {old_quantity} to {quantity}")
            else:
                # Create new item
                cart_item = CartItem.objects.create(
                    cart=cart,
                    product=product,
                    quantity=quantity
                )
                message = f'Item added with quantity {quantity}'
                action = 'added'
                print(f"Created new item with quantity: {quantity}")

        # Refresh the entire cart
        cart.refresh_from_db()

        # Use serializer
        serializer = CartSerializer(cart)
        response_data = serializer.data
        response_data['message'] = message
        response_data['action'] = action

        if quantity > 0:
            response_data['new_quantity'] = quantity

        # DEBUG: Print all items in cart after operation
        print(f"Checking all items in cart ID {cart.id} after update:")
        for item in cart.items.all():
            print(f"   - Product ID: {item.product.id}, Quantity: {item.quantity}")

        print(f"SUCCESS: Item {action}. Cart total items: {response_data.get('total_items', 0)}")

        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        print(f"ERROR in update_cart_item: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({'error': f'Failed to update item in cart: {str(e)}'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def remove_from_cart(request):
    """
    Remove item from cart
    """
    product_id = request.data.get('product_id')
    quantity = int(request.data.get('quantity', 1))

    print(f"DEBUG remove_from_cart: product_id={product_id}, quantity={quantity}")

    if not product_id:
        return Response({'error': 'Product ID is required'}, status=status.HTTP_400_BAD_REQUEST)

    if quantity < 1:
        return Response({'error': 'Quantity must be at least 1'}, status=status.HTTP_400_BAD_REQUEST)

    # Ensure session exists
    if not request.session.session_key:
        request.session.create()
    request.session.save()

    session_key = request.session.session_key

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

    # Find cart
    if request.user.is_authenticated:
        try:
            user_profile = request.user.userprofile
            cart = Cart.objects.filter(user=user_profile).first()
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)
    else:
        cart = Cart.objects.filter(session_key=session_key).first()

    if not cart:
        return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)

    # Find cart item
    cart_item = CartItem.objects.filter(cart=cart, product=product).first()

    if not cart_item:
        return Response({'error': 'Item not in cart'}, status=status.HTTP_404_NOT_FOUND)

    # Reduce quantity or remove
    if cart_item.quantity > quantity:
        cart_item.quantity -= quantity
        cart_item.save()
        message = f'Reduced quantity to {cart_item.quantity}'
    else:
        cart_item.delete()
        message = 'Item removed from cart'

    # Return updated cart
    cart_items = cart.items.all().select_related('product')
    total_price = cart.total_price()
    total_items = sum(item.quantity for item in cart_items)

    items_data = []
    for item in cart_items:
        product_data = {
            'id': item.product.id,
            'name': item.product.name,
            'price': float(item.product.price),
        }

        # Fix: Get the image URL string instead of the ImageFieldFile object
        if hasattr(item.product, 'image') and item.product.image:
            try:
                # Get the URL string representation
                product_data['image'] = request.build_absolute_uri(item.product.image.url)
            except (ValueError, AttributeError):
                # If there's no image or URL can't be built
                product_data['image'] = None
        else:
            product_data['image'] = None

        items_data.append({
            'id': item.id,
            'product': product_data,
            'quantity': item.quantity,
            'item_total': float(item.total_price())
        })

    response_data = {
        'id': cart.id,
        'items': items_data,
        'total_price': float(total_price),
        'total_items': total_items,
        'message': message
    }

    return Response(response_data, status=status.HTTP_200_OK)