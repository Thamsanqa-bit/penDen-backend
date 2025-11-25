from rest_framework import serializers
from .models import UserProfile
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'

class RegisterSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(write_only=True, required=True)
    email = serializers.CharField(write_only=True, required=True)
    address = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True, min_length=6)

    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'address', 'password']

    def validate_email(self, value):
        if UserProfile.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        # Extract custom fields BEFORE passing remaining data to User model
        phone = validated_data.pop('phone')
        address = validated_data.pop('address')
        email = validated_data.pop('email')
        password = validated_data.pop('password')

        # Create Django User
        user = User.objects.create_user(
            username=validated_data['username'],
            email=email,
            password=password
        )

        # Create UserProfile
        UserProfile.objects.create(
            user=user,
            email=email,
            phone=phone,
            address=address,
            password=make_password(password)
        )

        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
