from django.urls import path
from .views import product_list, upload_pdf

urlpatterns = [
    path("api/products/",product_list, name="product-list" ),
    path("api/upload-pdf/", upload_pdf, name="upload-pdf" ),
]