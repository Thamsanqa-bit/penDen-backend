from django.urls import path
from .views import product_list, upload_pdf, image_upload

urlpatterns = [
    path("products/",product_list, name="product-list" ),
    path("upload-pdf/", upload_pdf, name="upload-pdf" ),
    path("image-upload/",image_upload, name="image-upload"),
]