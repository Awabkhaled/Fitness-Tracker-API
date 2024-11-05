from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from .serializers import UserSerializer, AuthTokenSerializer


class CreateUserAPIView(generics.CreateAPIView):
    """Create a new user in the system"""
    serializer_class = UserSerializer


class AuthUserView(ObtainAuthToken):
    serializer_class = AuthTokenSerializer


class UpdateRetriveUserView(generics.RetrieveUpdateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        """retrieve and return the auth user"""
        return self.request.user
