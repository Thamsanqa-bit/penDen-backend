from django.shortcuts import render, redirect
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .models import Product
from rest_framework import status
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .serializers import ProductPDFSerializer, ProductSerializer, ImageSerializer
from rest_framework.permissions import IsAuthenticated
from accounts.models import UserProfile


from django_ratelimit.decorators import ratelimit
from django.core.cache import cache

from django.db.models import Q
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.paginator import Paginator
from django.db.models import Q
from django.core.cache import cache

from .models import Product
from .serializers import ProductSerializer


@api_view(['GET'])
def product_list(request):
    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 12))
    search = request.query_params.get('search', '').strip().lower()
    category = request.query_params.get('category', '').strip().lower()

    # ---- FAST + CLEAN CACHE KEY ----
    cache_key = f"p_{page}_{page_size}_s_{search}_c_{category}"
    cached_data = cache.get(cache_key)

    if cached_data:
        return Response(cached_data)

    # ---- OPTIMIZED QUERYSET ----
    products = Product.objects.select_related("category").all()

    # Filter by category
    if category:
        products = products.filter(category__name__iexact=category)

    # Search
    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(category__name__icontains=search)
        )

    products = products.order_by("id")

    # ---- PAGINATION ----
    paginator = Paginator(products, page_size)
    try:
        products_page = paginator.page(page)
    except:
        products_page = paginator.page(1)

    # ---- PASS REQUEST TO SERIALIZER SO IMAGE URL IS FULL S3 URL ----
    serializer = ProductSerializer(products_page, many=True, context={'request': request})

    response_data = {
        "products": serializer.data,
        "pagination": {
            "current_page": products_page.number,
            "total_pages": paginator.num_pages,
            "total_products": paginator.count,
            "has_next": products_page.has_next(),
            "has_previous": products_page.has_previous(),
            "next_page": products_page.next_page_number() if products_page.has_next() else None,
            "previous_page": products_page.previous_page_number() if products_page.has_previous() else None,
        },
    }

    cache.set(cache_key, response_data, timeout=300)  # 5 minutes cache
    return Response(response_data)

# @api_view(['GET'])
# def product_list(request):
#     page = request.query_params.get('page', 1)
#     page_size = request.query_params.get('page_size', 12)
#     search = request.query_params.get('search', '').strip()
#     category = request.query_params.get('category', '').strip()
#
#     cache_key = f'products_page_{page}_size_{page_size}_search_{search}_category_{category}'
#     cached = cache.get(cache_key)
#
#     if cached:
#         return Response(cached)
#
#     # Use prefetch_related to optimize database queries
#     products = Product.objects.prefetch_related('category').all()
#
#     # Filter by category if selected
#     if category:
#         products = products.filter(category__name__iexact=category)
#
#     # Search box still works
#     if search:
#         products = products.filter(
#             Q(name__icontains=search) | Q(category__name__icontains=search)
#         )
#
#     products = products.order_by("id")
#
#     paginator = Paginator(products, page_size)
#
#     try:
#         products_page = paginator.page(page)
#     except:
#         products_page = paginator.page(1)
#
#     serializer = ProductSerializer(products_page, many=True)
#
#     response_data = {
#         "products": serializer.data,
#         "pagination": {
#             "current_page": products_page.number,
#             "total_pages": paginator.num_pages,
#             "total_products": paginator.count,
#             "has_next": products_page.has_next(),
#             "has_previous": products_page.has_previous(),
#             "next_page": products_page.next_page_number() if products_page.has_next() else None,
#             "previous_page": products_page.previous_page_number() if products_page.has_previous() else None,
#         },
#     }
#
#     cache.set(cache_key, response_data, timeout=300)
#     return Response(response_data)

# @api_view(['GET'])
# @ratelimit(key='ip', rate='10/m', block=True)
# def product_list(request):
#     page = request.query_params.get('page', 1)
#     page_size = request.query_params.get('page_size', 12)  # Default 12 products per page
#     search = request.query_params.get('search', '').strip()
#
#     # Create cache key based on parameters
#     cache_key = f'products_page_{page}_size_{page_size}_search_{search}'
#     cached = cache.get(cache_key)
#
#     if cached:
#         return Response(cached)
#
#     if search:
#         products = Product.objects.filter(
#             Q(name__icontains=search) | Q(category__name__icontains=search)
#         ).order_by('id')
#     else:
#         products = Product.objects.all().order_by('id')
#
#     # Paginate the results
#     paginator = Paginator(products, page_size)
#
#     try:
#         products_page = paginator.page(page)
#     except PageNotAnInteger:
#         products_page = paginator.page(1)
#     except EmptyPage:
#         products_page = paginator.page(paginator.num_pages)
#
#     serializer = ProductSerializer(products_page, many=True)
#
#     response_data = {
#         'products': serializer.data,
#         'pagination': {
#             'current_page': products_page.number,
#             'total_pages': paginator.num_pages,
#             'total_products': paginator.count,
#             'has_next': products_page.has_next(),
#             'has_previous': products_page.has_previous(),
#             'next_page': products_page.next_page_number() if products_page.has_next() else None,
#             'previous_page': products_page.previous_page_number() if products_page.has_previous() else None,
#         }
#     }
#
#     cache.set(cache_key, response_data, timeout=300)
#     return Response(response_data)


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


def image_upload(request):
    user = UserProfile.objects.get(user=request.user)

    # Extract optional fields from POST
    email = request.data.get('email') or user.email
    phone = request.data.get('phone')

    if not email:
        return Response({'error': 'Missing email or phone'}, status=status.HTTP_400_BAD_REQUEST)

        # Merge user data into serializer
    data = request.data.copy()
    data['user'] = user.id
    data['email'] = email
    data['phone'] = phone

    serializer = ImageSerializer(data=data)
    if serializer.is_valid():
        serializer.save()

        return Response({
            "message": f"Thank you {user or ''}! Your image upload has been received. We will get back to you at {email} soon."
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
