from .models import Product, ProductListPDF
from rest_framework import serializers

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class ProductPDFSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductListPDF
        fields = ['id', 'title', 'pdf_file', 'uploaded_at']
        read_only_fields = ['uploaded_at']