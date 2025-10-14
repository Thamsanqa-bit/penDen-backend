from django.db import models
from products.models import Product
from accounts.models import UserProfile

# Create your models here.
class Order(models.Model):
    ORDER_SATUS = (
    ("Pending", "Pending"),
    ("Completed", "completed"),
    ("Canceled", "Canceled"),
    ("Out For Delivery", "Out For Delivery"),
    )

    order_status = models.CharField(max_length=255, choices=ORDER_SATUS, default="Pending")
    quantity = models.PositiveIntegerField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user_profile.user} {self.order_status}"
