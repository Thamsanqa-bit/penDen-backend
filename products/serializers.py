from .models import Product, ProductListPDF, ImageUpload
from rest_framework import serializers

# class ProductSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Product
#         fields = '__all__'
class ProductSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ["id","category", "name", "price", "category", "image", "order_status"]

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None

class ProductPDFSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductListPDF
        fields = ['id', 'title', 'pdf_file', 'uploaded_at']
        read_only_fields = ['uploaded_at']

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageUpload
        fields = ['id', 'image', 'uploaded_at']
        read_only_fields = ['uploaded_at']