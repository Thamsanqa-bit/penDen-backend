from django.db import models
from products.models import Product
from accounts.models import UserProfile

# Create your models here.
class Cart(models.Model):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "cart"

    def __str__(self):
        if self.user:
            return f"Cart ({self.user})"
        return f"Guest Cart ({self.session_key})"


    def total_price(self):
        return sum(item.total_price() for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = "cart_item"

    def __str__(self):
        return f"{self.product.name}: {self.product.price} and quantity: {self.quantity}"

    def total_price(self):
        return self.product.price * self.quantity

