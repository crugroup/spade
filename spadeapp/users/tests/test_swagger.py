import pytest
from django.urls import reverse

RESPONSE_OK = 200
RESPONSE_UNAUTHORIZED = 401


def test_swagger_accessible_by_admin(admin_client):
    url = reverse("swagger-ui")
    response = admin_client.get(url)
    assert response.status_code == RESPONSE_OK


@pytest.mark.django_db
def test_swagger_ui_not_accessible_by_normal_user(client):
    url = reverse("swagger-ui")
    response = client.get(url)
    assert response.status_code == RESPONSE_UNAUTHORIZED


def test_api_schema_generated_successfully(admin_client):
    url = reverse("schema")
    response = admin_client.get(url)
    assert response.status_code == RESPONSE_OK
