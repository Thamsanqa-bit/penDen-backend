from django.db import models

from orders import default_app_config
from .storage import OverwriteS3Boto3Storage

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

    class Meta:
        db_table = "categories"

class Product(models.Model):
    ORDER_STATUS = (
        ("pending", "Pending"),
        ("canceled", "Canceled"),
        ("delivered", "Delivered"),
        ("out-for-delivery", "Out For Delivery"),
    )

    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    order_status = models.CharField(max_length=20,choices=ORDER_STATUS,default="pending")
    image = models.ImageField(storage=OverwriteS3Boto3Storage(), upload_to='')

    class Meta:
        db_table = "products"

    def __str__(self):
        return self.name

class ProductListPDF(models.Model):
    title = models.CharField(max_length=100)
    pdf_file = models.FileField(upload_to='product_pdfs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
