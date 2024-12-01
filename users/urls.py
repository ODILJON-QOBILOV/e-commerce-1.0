from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from users.views import UserRegisterAPIView, UserLoginAPIView, GetUserAPIView

urlpatterns = [
    path('register/', UserRegisterAPIView.as_view()),
    path('login/', UserLoginAPIView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('get-me/', GetUserAPIView.as_view()),
]