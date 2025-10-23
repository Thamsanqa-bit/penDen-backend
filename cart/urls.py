from django.urls import path
from .views import get_cart, add_to_cart, remove_from_cart, update_cart

urlpatterns = [
    path("api/cart/", get_cart, name='get-cart'),
    path('api/cart/add/', add_to_cart, name='add-cart'),
    path('api/cart/remove/', remove_from_cart, name='remove_from_cart'),
    path('api/cart/update/', update_cart, name='update_cart'),
]