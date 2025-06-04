from django.urls import path
from .views import *



urlpatterns = [
  path('register/', UserRegistrationView.as_view(), name='register'),
  path('login/', UserLoginView.as_view(), name='login'),
  path('logout/', UserLogoutView.as_view(), name='logout'),
  path('update-user-details/', UpdateUserDetailsView.as_view(), name='update-user-details')
]