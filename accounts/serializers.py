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

    def create(self, validated_data):
        phone = validated_data.pop('phone')
        address = validated_data.pop('address')
        password = validated_data.pop('password')
        email = validated_data.pop('email')

        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()

        hashed_password = make_password(password)

        UserProfile.objects.create(user=user,
                                   email=email,
                                   phone=phone,
                                   address=address,
                                   password=hashed_password)
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
