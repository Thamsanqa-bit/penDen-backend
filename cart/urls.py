from django.urls import path
from . import views

urlpatterns = [
    path("api/cart/", views.get_cart, name='get-cart'),
    path('api/cart/add/', views.add_to_cart, name='add-cart'),
]