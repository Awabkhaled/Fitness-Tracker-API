"""The endpoints for the user application"""
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from .serializers import UserSerializer, AuthTokenSerializer
from drf_spectacular.utils import extend_schema


class CreateUserAPIView(generics.CreateAPIView):
    """Creating user with the provided info"""
    serializer_class = UserSerializer


class AuthUserView(ObtainAuthToken):
    """Obtaining a token for the user with provided info"""
    serializer_class = AuthTokenSerializer


@extend_schema(
    methods=['GET'],
    description="Retrieving information for the currently authenticated user."
)
@extend_schema(
    methods=['PUT', 'PATCH'],
    description="Updating information for the currently authenticated user."
)
class UpdateRetriveUserView(generics.RetrieveUpdateAPIView):
    """
    - Updating info for the current logined user
    - Retrieving info for the current logined user"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        """retrieve and return the auth user"""
        return self.request.user
