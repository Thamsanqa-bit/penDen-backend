import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from products.models import Product
from accounts.models import User, UserProfile
from cart.models import Cart, CartItem
from products.models import Category



@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_and_profile(db):
    user = User.objects.create_user(username="testuser", password="testpass123")
    profile = UserProfile.objects.create(user=user, address="123 Street", phone= "1223456", email="emailtest")
    return user, profile


# @pytest.fixture
# def product(db):
#     return Product.objects.create(name="Test Product", price=100.00)
@pytest.fixture
def product(db):
    category = Category.objects.create(name="Test Category")
    return Product.objects.create(
        name="Test Product",
        price=100.00,
        category=category
    )


@pytest.fixture
def auth_client(api_client, user_and_profile):
    user, _ = user_and_profile
    # api_client.login(username="testuser", password="testpass123")
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def urls():
    return {
        "add": reverse("add_cart"),
        "remove": reverse("remove_from_cart"),
        "get": reverse("get_cart"),
        "update": reverse("update_cart"),
    }


def test_add_to_cart_authenticated(auth_client, urls, product):
    """User can add product to their cart"""
    response = auth_client.post(urls["add"], {"product_id": product.id, "quantity": 2})
    assert response.status_code == status.HTTP_200_OK
    item = CartItem.objects.first()
    assert item.quantity == 2
    assert item.product == product


def test_get_cart(auth_client, urls, user_and_profile):
    """User can view their cart"""
    user, profile = user_and_profile
    Cart.objects.create(user=profile)
    response = auth_client.get(urls["get"])
    assert response.status_code == status.HTTP_200_OK
    assert "items" in response.data


def test_remove_from_cart(auth_client, urls, user_and_profile, product):
    """User can remove item from cart"""
    _, profile = user_and_profile
    cart = Cart.objects.create(user=profile)
    CartItem.objects.create(cart=cart, product=product, quantity=1)

    response = auth_client.post(urls["remove"], {"product_id": product.id, "quantity": 1})
    assert response.status_code == status.HTTP_200_OK

    # Check that the cart item was completely removed
    item = CartItem.objects.first()
    assert item is None  # Item should be completely removed when quantity reaches 0

    # OR if you want to verify the cart still exists but has no items
    cart.refresh_from_db()
    assert cart.items.count() == 0  # No items in cart


def test_update_cart_quantity(auth_client, urls, user_and_profile, product):
    """User can update cart item quantity"""
    _, profile = user_and_profile
    cart = Cart.objects.create(user=profile)
    CartItem.objects.create(cart=cart, product=product, quantity=1)

    response = auth_client.put(urls["update"], {"product_id": product.id, "quantity": 5})
    assert response.status_code == status.HTTP_200_OK

    item = CartItem.objects.first()
    item.refresh_from_db()
    assert item.quantity == 5


def test_add_to_cart_invalid_product(auth_client, urls):
    """Handle invalid product IDs gracefully"""
    response = auth_client.post(urls["add"], {"product_id": 9999, "quantity": 1})
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "error" in response.data


def test_guest_add_to_cart(api_client, urls, product):
    """Guests can add items via session"""
    response = api_client.post(urls["add"], {"product_id": product.id, "quantity": 1})
    assert response.status_code == status.HTTP_200_OK
    assert Cart.objects.filter(session_key__isnull=False).exists()


# from django.urls import reverse
# from rest_framework.test import APITestCase, APIClient
# from rest_framework import status
# from products.models import Product
# from accounts.models import User, UserProfile
# from .models import Cart, CartItem
#
# class CartTestCase(APITestCase):
#     def setUp(self):
#         #create user and user profile
#         self.user = User.objects.create_user(username='testuser', password='test1234567')
#         self.user_profile = UserProfile.objects.create(user=self.user, address='testaddress', phone='testphone', email='testemail')
#
#         #create product
#         self.product = Product.objects.create(name='testproduct', price=25.00)
#
#         #authenticate client
#         self.client = APIClient()
#         self.client.login(username='testuser', password='test1234567')
#
#         #endpoint
#         self.add_url = reverse('add_cart')
#         self.remove_url = reverse('remove_from_cart')
#         self.update_url = reverse('update_cart')
#         self.cart_url = reverse('get_cart')
#
#     def test_add_to_cart_authentication(self):
#         #ensure user can add to cart
#         response = self.client.pst(self.add_url, {'product_id': self.product.id, 'quantity': 2})
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(CartItem.objects.count(), 1)
#         self.assertEqual(CartItem.objects.first().quantity, 2)
#
#     def test_get_cart_item(self):
#         # ensure user can retrieve their cart
#         Cart.objects.create(user=self.user_profile)
#         response = self.client.get(self.cart_url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertIn('Item', response.data)
#
#     def test_remove_from_cart_authentication(self):
#         #ensure user can remove items
#         cart = Cart.objects.create(user=self.user_profile)
#         CartItem.objects.create(cart=cart, product=self.product, quantity=1)
#
#
#         response = self.client.post(self.remove_url, {'product_id': self.product.id, 'quantity': 1})
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#
#         cart_item = CartItem.objects.first()
#         self.assertEqual(cart_item.quantity, 2)
#
#     def test_update_cart_quantity(self):
#         """Ensure cart item quantity can be updated"""
#         cart = Cart.objects.create(user=self.user_profile)
#         item = CartItem.objects.create(cart=cart, product=self.product, quantity=1)
#
#         response = self.client.put(self.update_url, {"product_id": self.product.id, "quantity": 5})
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         item.refresh_from_db()
#         self.assertEqual(item.quantity, 5)
#
#     def test_add_to_cart_invalid_product(self):
#         """Handle invalid product gracefully"""
#         response = self.client.post(self.add_url, {"product_id": 9999, "quantity": 1})
#         self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
#         self.assertIn("error", response.data)
#
#     def test_guest_add_to_cart(self):
#         """Ensure guest user cart works via session"""
#         guest_client = APIClient()
#         response = guest_client.post(self.add_url, {"product_id": self.product.id, "quantity": 1})
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertTrue(Cart.objects.filter(session_key__isnull=False).exists())

