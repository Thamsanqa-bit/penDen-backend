# shop/utils.py

from cart.models import Cart, CartItem

def merge_guest_cart_with_user_cart(session_key, user):
    try:
        guest_cart = Cart.objects.get(session_key=session_key, user__isnull=True)
    except Cart.DoesNotExist:
        return  # No guest cart found

    # Get or create the user cart
    user_cart, _ = Cart.objects.get_or_create(user=user)

    for item in guest_cart.cartitem_set.all():
        # Move items to user cart
        user_item, created = CartItem.objects.get_or_create(
            cart=user_cart,
            product=item.product
        )
        if created:
            user_item.quantity = item.quantity
        else:
            user_item.quantity += item.quantity
        user_item.save()

    # Delete guest cart
    guest_cart.delete()
