from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView



urlpatterns = [
  path('register/', UserRegistrationView.as_view(), name='register'),
  path('login/', UserLoginView.as_view(), name='login'),
  path('logout/', UserLogoutView.as_view(), name='logout'),
  path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
  path('update-user-details/', UpdateUserDetailsView.as_view(), name='update-user-details'),
  path('change-password/', ChangePasswordView.as_view(), name='change-password'),
]