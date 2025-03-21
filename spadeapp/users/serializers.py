from django.contrib.auth.models import Group, Permission
from django.core.validators import EmailValidator
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User

logger = __import__("logging").getLogger(__name__)


class RegisterUserSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField()
    email = serializers.EmailField(validators=[EmailValidator(), UniqueValidator(queryset=User.objects.all())])

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "password", "token"]
        extra_kwargs = {
            "password": {"write_only": True, "min_length": 8},
        }

    def get_token(self, user) -> dict[str, str]:
        token = RefreshToken.for_user(user)
        data = {"refresh": str(token), "access": str(token.access_token)}
        return data


class UserSerializer(serializers.ModelSerializer):
    """Use this serializer to get the user profile"""

    class Meta:
        model = User
        fields = ["id", "is_active", "first_name", "last_name", "email", "groups", "user_permissions"]


class TokenSerializer(serializers.ModelSerializer):
    token = serializers.CharField(source="key")

    class Meta:
        model = Token
        fields = ["token"]


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["id", "name", "permissions"]


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ["id", "name", "codename"]
