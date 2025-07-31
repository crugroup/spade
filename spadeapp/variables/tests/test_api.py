import pytest
from django.urls import reverse
from rest_framework import status

from spadeapp.users.models import User
from spadeapp.variables.models import Variable


@pytest.fixture
def user():
    """Create and return a regular user."""
    return User.objects.create_user(
        email="test@example.com",
        password="testpassword",
    )


@pytest.fixture
def regular_variable():
    """Create and return a non-secret variable."""
    return Variable.objects.create(
        name="regular_var",
        description="Regular variable",
        value="regular_value",
        is_secret=False,
    )


@pytest.fixture
def secret_variable():
    """Create and return a secret variable."""
    return Variable.objects.create(
        name="secret_var",
        description="Secret variable",
        value="secret_value",
        is_secret=True,
    )


@pytest.fixture
def variables_url():
    """Return the URL for the variable list endpoint."""
    return reverse("api:variable-list")


@pytest.mark.django_db
class TestVariableAPI:
    def test_create_variable(self, client, variables_url):
        """Test creating variables."""
        # Create a regular variable
        data = {
            "name": "new_regular_var",
            "description": "New regular variable",
            "value": "new_value",
            "is_secret": False,
        }
        response = client.post(variables_url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Variable.objects.count() == 1

        # Create a secret variable
        data = {
            "name": "new_secret_var",
            "description": "New secret variable",
            "value": "secret_value",
            "is_secret": True,
        }
        response = client.post(variables_url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Variable.objects.count() == 2  # noqa: PLR2004

    def test_update_variable_is_secret_field(self, client, regular_variable, secret_variable):
        """Test that is_secret field cannot be modified after creation."""
        # Try to update regular variable to make it secret
        regular_view_url = reverse("api:variable-view", kwargs={"pk": regular_variable.pk})
        data = {"is_secret": True}
        response = client.patch(regular_view_url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        # Verify the variable was not updated
        regular_variable.refresh_from_db()
        assert regular_variable.is_secret is False

        # Try to update secret variable to make it non-secret
        secret_view_url = reverse("api:variable-view", kwargs={"pk": secret_variable.pk})
        data = {"is_secret": False}
        response = client.patch(secret_view_url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        # Verify the variable was not updated
        secret_variable.refresh_from_db()
        assert secret_variable.is_secret is True

    def test_update_other_fields(self, client, regular_variable):
        """Test that other fields can still be updated."""
        # Update name and description of regular variable
        regular_view_url = reverse("api:variable-view", kwargs={"pk": regular_variable.pk})
        data = {"name": "updated_regular_var", "description": "Updated description"}
        response = client.patch(regular_view_url, data)
        assert response.status_code == status.HTTP_200_OK

        # Verify the variable was updated
        regular_variable.refresh_from_db()
        assert regular_variable.name == "updated_regular_var"
        assert regular_variable.description == "Updated description"
        assert regular_variable.is_secret is False  # This should remain unchanged
