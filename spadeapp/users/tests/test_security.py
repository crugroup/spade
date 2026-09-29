import pytest
from django.contrib.auth.models import Group, Permission
from rest_framework import status
from rest_framework.test import APIClient

from spadeapp.users.models import User
from spadeapp.users.tests.factories import UserFactory


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def normal_user(db):
    user = UserFactory()
    user.is_superuser = False
    user.is_staff = False
    user.save()
    return user


class TestProfileUpdate:
    def test_cannot_escalate_own_permissions(self, api_client, normal_user):
        group = Group.objects.create(name="admins")
        permission_ids = list(Permission.objects.values_list("id", flat=True))
        original_email = normal_user.email
        api_client.force_authenticate(user=normal_user)

        resp = api_client.patch(
            "/api/v1/users/me",
            {
                "user_permissions": permission_ids,
                "groups": [group.id],
                "is_active": False,
                "email": "attacker@example.com",
            },
            format="json",
        )

        assert resp.status_code == status.HTTP_200_OK
        normal_user.refresh_from_db()
        assert normal_user.user_permissions.count() == 0
        assert normal_user.groups.count() == 0
        assert normal_user.is_active is True
        assert normal_user.email == original_email
        assert not User.objects.get(pk=normal_user.pk).has_perm("users.change_user")

    def test_can_update_own_name(self, api_client, normal_user):
        api_client.force_authenticate(user=normal_user)

        resp = api_client.patch("/api/v1/users/me", {"first_name": "Renamed"}, format="json")

        assert resp.status_code == status.HTTP_200_OK
        normal_user.refresh_from_db()
        assert normal_user.first_name == "Renamed"


class TestRegistration:
    payload = {
        "first_name": "New",
        "last_name": "User",
        "email": "new.user@example.com",
        "password": "a-long-password-123",
    }

    def test_closed_registration_rejected(self, db, api_client, settings):
        settings.ACCOUNT_ALLOW_REGISTRATION = False

        resp = api_client.post("/api/v1/registration", self.payload, format="json")

        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert not User.objects.filter(email=self.payload["email"]).exists()

    def test_open_registration_allowed(self, db, api_client, settings):
        settings.ACCOUNT_ALLOW_REGISTRATION = True

        resp = api_client.post("/api/v1/registration", self.payload, format="json")

        assert resp.status_code == status.HTTP_201_CREATED, resp.content[:300]
        assert User.objects.filter(email=self.payload["email"]).exists()
