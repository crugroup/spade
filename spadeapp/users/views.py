from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

from .serializers import RegisterUserSerializer, TokenSerializer, UserSerializer

User = get_user_model()


class RegisterUserView(generics.CreateAPIView):
    """Register a new user and return a token for the user"""

    permission_classes = [permissions.AllowAny]
    throttle_classes = [AnonRateThrottle]
    serializer_class = RegisterUserSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        token = serializer.get_token(user)
        serializer.validated_data["token"] = token
        return super().perform_create(serializer)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Get and update user profile"""

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    def get_object(self):
        return self.request.user


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """Get a user"""

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()
    search_fields = ("first_name", "last_name")
    filterset_fields = ("first_name", "last_name")


class ObtainTokenView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TokenSerializer

    def get_object(self):
        Token.objects.filter(user=self.request.user).delete()
        token, created = Token.objects.get_or_create(user=self.request.user)
        return token
