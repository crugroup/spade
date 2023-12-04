from django.contrib.auth import get_user_model
from rest_framework import serializers

from spadeapp.users.models import User as UserType

User = get_user_model()


class UserSerializer(serializers.ModelSerializer[UserType]):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "email"]
        fields = ["id", "first_name", "last_name", "email"]

        extra_kwargs = {
            "url": {"view_name": "api:user-detail", "lookup_field": "pk"},
        }
