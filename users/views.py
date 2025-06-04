from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework import status
from rest_framework.views import APIView
from .utils import *
from .serializers import *

#--------------- User Registration ---------------

class UserRegistrationView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        try:
            if serializer.is_valid():
                user = serializer.save()
                response_data = {
                    'status': 'success',
                    'message': 'User registered successfully',
                    'data': {
                        'email': user.email,
                        'username': user.username,
                    },
                    
                }
                return Response(response_data, status=status.HTTP_201_CREATED)
            
            return Response({
                'status': 'error',
                'message': 'Validation failed',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({
                'status': 'error',
                'message': 'An unexpected error occurred during registration. Please try again later.',
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)   
        


class UserLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        password = request.data.get('password', '')

        if not email or not password:
            return Response({
                'status': 'error',
                'message': 'Email and password are required.',
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate email format
        try:
            validate_email(email)
        except EmailFormateError:
            return Response({
                'status': 'error',
                'message': 'Invalid email format.',
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check if user exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'No account found with this email address.',
            }, status=status.HTTP_401_UNAUTHORIZED)

        # Authenticate user
        user = authenticate(request=request, email=email, password=password)

        if not user:
            return Response({
                'status': 'error',
                'message': 'Invalid credentials.',
            }, status=status.HTTP_401_UNAUTHORIZED)

        # Generate tokens and return 
        refresh = RefreshToken.for_user(user)
        return Response({
            'status': 'success',
            'message': 'Login successful',
            'data': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'email': user.email,
                'username': user.username,
            }
        }, status=status.HTTP_200_OK)




class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token :
            return Response({
                "status": "error",
                "message": "Refresh token is required."
            },status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({
                "status": "success",
                "message": "You are successfully logged out"
            }, status=status.HTTP_200_OK) 
        
        except TokenError as e :
            return Response({
                "status": "error",
                "message": "Invalid or expired token.",
                "details": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)



class UpdateUserDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        print('user ssss',request.user)
        serializer = UserUpdateSerializer(user, data=request.data, context={'request': request})  

        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": "success",
                "message": "User details updated successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "status": "error",
            "message": "Update failed.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({
                "status": "success",
                "message": "Password changed successfully."
            }, status=status.HTTP_200_OK)
        
        return Response({
            "status": "error",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)