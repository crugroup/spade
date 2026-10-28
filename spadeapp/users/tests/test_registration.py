from unittest.mock import patch

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from spadeapp.users.models import User
from spadeapp.users.serializers import RegisterUserSerializer


@pytest.mark.django_db
def test_registration_saves_user_once():
    payload = {"first_name": "New", "last_name": "User", "email": "new@example.com", "password": "a-long-password-1"}

    with patch.object(RegisterUserSerializer, "update") as update:
        resp = APIClient().post("/api/v1/registration", payload, format="json")

    assert resp.status_code == status.HTTP_201_CREATED, resp.content[:300]
    update.assert_not_called()
    user = User.objects.get(email=payload["email"])
    assert user.check_password(payload["password"])
    assert set(resp.json()["token"]) == {"refresh", "access"}
