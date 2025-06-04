import re
from django.core.validators import validate_email as validate_email_format
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import User 


def validate_custom_email(value, current_user=None):
    value = value.strip().lower()
    try:
        validate_email_format(value)
    except:
        raise serializers.ValidationError("Enter a valid email address.")    
    
    qs = User.objects.filter(email=value)
    if current_user:
        qs = qs.exclude(id=current_user.id)
    if qs.exists():
        raise serializers.ValidationError("This email with user already exist.")
    return value



def validate_custom_username(value, current_user=None):
    value = value.strip()
    reserved_usernames = ['admin', 'support', 'root', 'user', 'unknown', 'system', 'null']

    if not (4 <= len(value) <= 50):
        raise serializers.ValidationError("Username must be between 4 and 50 characters.")
    if not re.match(r'^[a-zA-Z0-9_]+$', value):
        raise serializers.ValidationError("Username can only contain alphanumeric characters and underscores.")
    if re.fullmatch(r'_+', value):
        raise serializers.ValidationError("Username cannot contain only underscores.")
    if value.isdigit():
        raise serializers.ValidationError("Username cannot contain only numbers.")
    if not re.search(r'[a-zA-Z]', value):
        raise serializers.ValidationError("Username must include at least one letter.")
    if value.startswith('_') or value.endswith('_'):
        raise serializers.ValidationError("Username cannot start or end with an underscore.")
    if '__' in value:
        raise serializers.ValidationError("Username cannot contain consecutive underscores.")
    if '@' in value or '.' in value:
        raise serializers.ValidationError("Username cannot look like an email or contain '.' or '@'.")
    if value.lower() in reserved_usernames:
        raise serializers.ValidationError("This username is not allowed.")

    qs = User.objects.filter(username__iexact=value)
    if current_user:
        qs = qs.exclude(id=current_user.id)
    if qs.exists():
        raise serializers.ValidationError("A user with this username already exists.")
    return value



def validate_password_strength(password):
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 char long")
    if not re.search(r"[A-Z]", password):
        raise ValidationError("Password must contain at least one uppercase letter.")
    if not re.search(r"[a-z]", password):
        raise ValidationError("Password must contain at least one lowercase letter.")
    if not re.search(r"\d", password):
        raise ValidationError("Password must contain at least one digit.")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise ValidationError("Password must contain at least one special character.")
    return password  