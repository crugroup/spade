from allauth.account import app_settings as allauth_account_settings
from allauth.account.utils import complete_signup
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group, Permission
from rest_framework import generics, permissions, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

from .serializers import (
    GroupSerializer,
    RegisterUserSerializer,
    TokenSerializer,
    UserPermissionSerializer,
    UserSerializer,
)

User = get_user_model()


class RegisterUserView(generics.CreateAPIView):
    """Register a new user and return a token for the user"""

    permission_classes = [permissions.AllowAny]
    throttle_classes = [AnonRateThrottle]
    serializer_class = RegisterUserSerializer

    def perform_create(self, serializer):
        serializer.validated_data["password"] = make_password(serializer.validated_data["password"])
        user = serializer.save()
        token = serializer.get_token(user)
        serializer.validated_data["token"] = token
        result = super().perform_create(serializer)
        complete_signup(
            self.request._request,
            user,
            allauth_account_settings.EMAIL_VERIFICATION,
            None,
        )
        return result


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Get and update user profile"""

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    def get_object(self):
        return self.request.user


class UserViewSet(viewsets.ModelViewSet):
    """Get a user"""

    serializer_class = UserSerializer
    permission_classes = [permissions.DjangoModelPermissions]
    queryset = User.objects.all()
    search_fields = ("first_name", "last_name", "email")
    filterset_fields = ("first_name", "last_name", "email")


class ObtainTokenView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TokenSerializer

    def get_object(self):
        Token.objects.filter(user=self.request.user).delete()
        token, created = Token.objects.get_or_create(user=self.request.user)
        return token


class GroupViewSet(viewsets.ModelViewSet):
    """Get a user"""

    serializer_class = GroupSerializer
    permission_classes = [permissions.DjangoModelPermissions]
    queryset = Group.objects.all()
    search_fields = ("name",)
    filterset_fields = ("name",)


class UserPermissionsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserPermissionSerializer
    queryset = Permission.objects.none()

    def get(self, request, *args, **kwargs):
        if request.user.is_superuser:
            serializer = UserPermissionSerializer((Permission(name="Is superuser", codename="*"),), many=True)
            return Response(serializer.data)

        user = request.user
        # Get the user's group permissions
        group_permissions = Permission.objects.filter(group__user=user)
        # Get the user's user permissions
        user_permissions = Permission.objects.filter(user=user)
        # Combine the querysets
        all_permissions = group_permissions.union(user_permissions)

        serializer = UserPermissionSerializer(all_permissions, many=True)
        return Response(serializer.data)
