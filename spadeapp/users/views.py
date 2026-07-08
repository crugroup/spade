from allauth.account import app_settings as allauth_account_settings
from allauth.account.utils import complete_signup
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group, Permission
from rest_framework import generics, permissions, views, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

from .models import UserFavorite
from .serializers import (
    GroupSerializer,
    PermissionSerializer,
    RegisterUserSerializer,
    TokenSerializer,
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
        token, _created = Token.objects.get_or_create(user=self.request.user)
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
    serializer_class = PermissionSerializer
    queryset = Permission.objects.none()

    def get(self, request, *args, **kwargs):
        if request.user.is_superuser:
            serializer = PermissionSerializer((Permission(name="Is superuser", codename="*"),), many=True)
            return Response(serializer.data)

        user = request.user
        # Get the user's group permissions
        group_permissions = Permission.objects.filter(group__user=user)
        # Get the user's user permissions
        user_permissions = Permission.objects.filter(user=user)
        # Combine the querysets
        all_permissions = group_permissions.union(user_permissions)

        serializer = PermissionSerializer(all_permissions, many=True)
        return Response(serializer.data)


class PermissionsView(generics.ListAPIView):
    """List all available permissions"""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PermissionSerializer
    queryset = Permission.objects.all()
    search_fields = ("name", "codename")
    filterset_fields = ("name", "codename")
    ordering_fields = ("name", "codename")
    ordering = ("name",)
    throttle_classes = [UserRateThrottle]
    pagination_class = None


class FavoritesView(views.APIView):
    """List, add, and remove user favorites."""

    permission_classes = [IsAuthenticated]
    ALLOWED_RESOURCES = {choice[0] for choice in UserFavorite.RESOURCE_CHOICES}

    def _validate_resource(self, resource):
        if resource not in self.ALLOWED_RESOURCES:
            return Response(
                {"error": f"Invalid resource. Must be one of: {sorted(self.ALLOWED_RESOURCES)}"},
                status=400,
            )
        return None

    def _coerce_resource_id(self, raw):
        try:
            return int(raw)
        except (TypeError, ValueError) as e:
            raise ValueError("resource_id must be an integer") from e

    def get(self, request):
        favorites = request.user.favorites.all().values("id", "resource", "resource_id", "label")
        return Response(list(favorites))

    def post(self, request):
        resource = request.data.get("resource")
        label = request.data.get("label", "")
        try:
            resource_id = self._coerce_resource_id(request.data.get("resource_id"))
        except ValueError as e:
            return Response({"error": str(e)}, status=400)

        if not resource or resource_id is None:
            return Response({"error": "resource and resource_id required"}, status=400)
        err = self._validate_resource(resource)
        if err:
            return err
        fav, _ = request.user.favorites.get_or_create(
            resource=resource,
            resource_id=resource_id,
            defaults={"label": label},
        )
        if not fav.label and label:
            fav.label = label
            fav.save(update_fields=["label"])
        return Response({"id": fav.id, "resource": fav.resource, "resource_id": fav.resource_id, "label": fav.label})

    def delete(self, request):
        resource = request.query_params.get("resource")
        try:
            resource_id = self._coerce_resource_id(request.query_params.get("resource_id"))
        except ValueError as e:
            return Response({"error": str(e)}, status=400)

        if not resource or resource_id is None:
            return Response({"error": "resource and resource_id required as query params"}, status=400)
        err = self._validate_resource(resource)
        if err:
            return err
        request.user.favorites.filter(resource=resource, resource_id=resource_id).delete()
        return Response(status=204)
