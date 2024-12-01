from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiExample

from users.models import User
from users.serializers import RegisterSerializer, LoginSerializer, UserSerializer


class UserRegisterAPIView(APIView):
    @extend_schema(
        request=RegisterSerializer,
        examples=[
            OpenApiExample(
                name="User Registration",
                value={
                    "username": "John",
                    "email": "johnolan@gmail.com",
                    "password": "<PASSWORD>",
                }

            )
        ]
    )
    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')

        if not username or not email or not password:
            return Response({'message': 'all 3 columns are required'})

        if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
            return Response({'message': 'User with this username or email already exists!'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        return Response({
            'message': 'User Successfully registered!',
            'refresh_token': str(refresh),
            'access_token': str(access)
        }, status=status.HTTP_201_CREATED)


class UserLoginAPIView(APIView):
    @extend_schema(
        request=LoginSerializer,
        examples=[
            OpenApiExample(
                name="User Login",
                value={
                    "username_or_email": "johnolan@gmail.com",
                    "password": "<PASSWORD>",
                }
            )
        ]
    )
    def post(self, request):
        username_or_email = request.data.get('username_or_email')
        password = request.data.get('password')

        if not username_or_email or not password:
            return Response({'message': 'all 2 columns are required'})

        if '@' in username_or_email:
            try:
                user = User.objects.get(email=username_or_email)
                username = user.username
            except:
                return Response({"message": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)

        else:
            username = username_or_email

        user = authenticate(username=username, password=password)
        if user is None:
            return Response({'message': 'Invalid username/email or password'}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token


        return Response({
            "message": "You are logged in Successfully",
            "refresh_token": str(refresh),
            "access_token": str(access)
        }, status=status.HTTP_202_ACCEPTED)

class GetUserAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)