from rest_framework import serializers
from .models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.validators import validate_email
from django.core.exceptions import  ValidationError as EmailFormateError
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from .validators import *
import re




class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'confirm_password']

    def validate_email(self, value):
        return validate_custom_email(value)

    def validate_username(self, value):
        return validate_custom_username(value)
    
    def validate_password(self, value):
        """
        Validates the strength of the password
        - at least 1 uppercase, 1 lowercase, 1 digit, 1 special character
        """
        validate_password_strength(value)
        return value
    
    def validate(self, attrs):
        
        if attrs.get("password") != attrs.get("confirm_password"):
            raise serializers.ValidationError("Passwords do not match.")
        return attrs
    
    def create(self, validated_data):
        
        validated_data.pop("confirm_password")
        user = User.objects.create_user(**validated_data)
        return user
   
    


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        email = data.get('email').strip().lower()
        password = data.get('password')

        if not email or not password:
            raise serializers.ValidationError("Email and password are required.")
        try:
            validate_email(email)
        
        except EmailFormateError:
            raise serializers.ValidationError("Invalid email format.")
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise AuthenticationFailed("Invalid email or password.")
        
        user = authenticate(request=self.context.get('request'), email=user.email, password=password)
        
        if not user:
            raise AuthenticationFailed("Invalid credentials")

        
        return user
    


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'username']

    def validate_email(self, value):
        return validate_custom_email(value, self.context['request'].user)

    def validate_username(self, value):
        return validate_custom_username(value, self.context['request'].user)



class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_password  = serializers.CharField(write_only=True)

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("The current password you entered is incorrect. Please try again.")
        return value
    
    def validate_new_password(self, value):
        return validate_password_strength(value)
    
    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("New password and confirm password do not match.")
        return data
