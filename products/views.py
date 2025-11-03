from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Product
from .serializers import ProductSerializer

from django_ratelimit.decorators import ratelimit
from django.core.cache import cache

from django.db.models import Q

@api_view(['GET'])
@ratelimit(key='ip', rate='10/m', block=True)
def product_list(request):
    cached = cache.get('products')
    if cached:
        return Response(cached)

    search = request.query_params.get('search', '').strip()

    if search:
        products = Product.objects.filter(
            Q(name__icontains=search) | Q(category__name__icontains=search)
        )
    else:
        products = Product.objects.all()

    serializer = ProductSerializer(products, many=True)
    cache.set('products', serializer.data, timeout=300)
    return Response(serializer.data)
