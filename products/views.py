from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Product
from .serializers import ProductSerializer

# Create your views here.
@api_view(['GET'])
def product_list(request):
    search = request.query_params.get('search', '')  # ?search=category_name
    if search:
        products = Product.objects.filter(category__icontains=search)
    else:
        products = Product.objects.all()

    serializer = ProductSerializer(products, many=True)
    # return Response({
    #     "count": products.count(),
    #     "products": serializer.data
    # })
    return Response(serializer.data)
