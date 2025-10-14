from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import UserProfile
from .serializers import UserProfileSerializer

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
