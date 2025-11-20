from django.shortcuts import render, redirect
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .models import Product
from rest_framework import status
from .serializers import ProductPDFSerializer, ProductSerializer
from rest_framework.permissions import IsAuthenticated
from accounts.models import UserProfile


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

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_pdf(request):
    user = UserProfile.objects.get(user=request.user)
    # Extract optional fields from POST
    email = request.data.get('email') or user.email
    phone = request.data.get('phone')

    # Ensure email exists
    if not email:
        return Response({'error': 'Missing email or phone'}, status=status.HTTP_400_BAD_REQUEST)

    # Merge user data into serializer
    data = request.data.copy()
    data['user'] = user.id
    data['email'] = email
    data['phone'] = phone


    serializer = ProductPDFSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "message": f"Thank you {user or ''}! Your product list has been received. We will get back to you at {email} soon."
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
