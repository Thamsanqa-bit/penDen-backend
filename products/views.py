from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Product
from .serializers import ProductSerializer

from django.db.models import Q

@api_view(['GET'])
def product_list(request):
    search = request.query_params.get('search', '').strip()

    if search:
        products = Product.objects.filter(
            Q(name__icontains=search) | Q(category__name__icontains=search)
        )
    else:
        products = Product.objects.all()

    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)
