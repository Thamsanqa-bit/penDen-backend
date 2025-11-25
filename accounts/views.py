from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import UserProfile
from .serializers import UserProfileSerializer
from rest_framework.authtoken.models import Token
from rest_framework import status
from django.contrib.auth import authenticate
from .serializers import RegisterSerializer, LoginSerializer
from cart.utils import merge_guest_cart_with_user_cart
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)  # cache for 15 minutes

@api_view(['POST'])
def register(request):
    serializer = RegisterSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            "message": "User registered successfully",
            "token": token.key,
            "username": user.username,
            "email": user.email,
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['POST'])
# def register(request):
#     serializer = RegisterSerializer(data=request.data)
#     #hash password
#
#     if serializer.is_valid():
#         user = serializer.save()
#
#         token, _ = Token.objects.get_or_create(user=user)
#         return Response({
#             'message': 'User registered successfully',
#             'token': token.key,
#             'username': user.username,
#             'email': user.email,
#         }, status=status.HTTP_201_CREATED)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login_user(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        user = authenticate(username=username, password=password)

        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'status': 'success',
                'message': 'User logged in successfully',
                'token': token.key,
                'user': {
                    'username': user.username,
                    'email': user.email,
                }
            }, status=status.HTTP_200_OK)

        return Response({
            'status': 'error',
            'message': 'Invalid username or password',
        }, status=status.HTTP_401_UNAUTHORIZED)

    return Response({
        'status': 'error',
        'message': 'Invalid input data',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['POST'])
# def login_user(request):
#     serializer = LoginSerializer(data=request.data)
#     if serializer.is_valid():
#         username = serializer.validated_data['username']
#         password = serializer.validated_data['password']
#
#         user = authenticate(username=username, password=password)
#
#         if user:
#             token, created = Token.objects.get_or_create(user=user)
#             return Response({
#                 'message':'User logged in Successfully',
#                 'token': token.key,
#                 'username': user.username,
#                 'email': user.email,
#             }, status=status.HTTP_200_OK)
#         return Response({
#             'message':'Invalid credentials',
#
#         },status=status.HTTP_401_UNAUTHORIZED)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_profile_view(request):
    try:
        # Try to get existing profile
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        # Create new profile if none exists
        user_profile = UserProfile.objects.create(
            user=request.user,
            phone=request.data.get('phone', ''),
            address=request.data.get('address', ''),
        )

    serializer = UserProfileSerializer(user_profile)
    return Response(serializer.data)
