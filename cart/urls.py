from django.urls import path
from .views import get_cart, add_to_cart, remove_from_cart, update_cart_item

urlpatterns = [
    path("cart/", get_cart, name='get_cart'),
    path('cart/add/', add_to_cart, name='add_cart'),
    path('cart/remove/', remove_from_cart, name='remove_from_cart'),
    path('cart/update/', update_cart_item, name='update_cart'),
]