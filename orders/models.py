from django.db import models
from products.models import Product
from accounts.models import UserProfile

class Order(models.Model):
    ORDER_STATUS = (
        ("Pending", "Pending"),
        ("Completed", "Completed"),
        ("Canceled", "Canceled"),
        ("Out For Delivery", "Out For Delivery"),
    )

    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    order_status = models.CharField(max_length=255, choices=ORDER_STATUS, default="Pending")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "orders"

    def __str__(self):
        return f"Order #{self.id} - {self.user.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        db_table = "order_item"

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"