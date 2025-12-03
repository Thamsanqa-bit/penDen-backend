from django.db import models
from products.models import Product
from accounts.models import UserProfile

class Cart(models.Model):
    user = models.OneToOneField(
        UserProfile,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        unique=True  # Each user can have only one cart
    )
    session_key = models.CharField(
        max_length=40,
        null=True,
        blank=True,
        unique=True  # Each session can have only one cart
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "cart"
        # Add constraint to ensure either user or session_key is set
        constraints = [
            models.CheckConstraint(
                check=models.Q(user__isnull=False) | models.Q(session_key__isnull=False),
                name='user_or_session_required'
            )
        ]

    def __str__(self):
        if self.user:
            return f"Cart ({self.user})"
        return f"Guest Cart ({self.session_key})"

    def total_price(self):
        return sum(item.total_price() for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = "cart_item"
        unique_together = ['cart', 'product']  # Prevent duplicate products in cart

    def __str__(self):
        return f"{self.product.name}: {self.product.price} and quantity: {self.quantity}"

    def total_price(self):
        return self.product.price * self.quantity