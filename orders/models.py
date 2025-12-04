# models.py - Update Order model
from django.db import models
from django.contrib.auth.models import User

class Order(models.Model):
    ORDER_STATUS = (
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("canceled", "Canceled"),
    )

    user = models.ForeignKey('accounts.UserProfile', on_delete=models.SET_NULL, null=True, blank=True)  # Allow null for guests
    session_id = models.CharField(max_length=255, blank=True, null=True)  # Store session ID for guest users
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    address = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=ORDER_STATUS, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'orders'
        ordering = ['-created_at']

    def __str__(self):
        if self.user:
            return f"Order #{self.id} by {self.user.user.username}"
        else:
            return f"Order #{self.id} (Guest - Session: {self.session_id})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)  # String reference
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'order_items'

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


