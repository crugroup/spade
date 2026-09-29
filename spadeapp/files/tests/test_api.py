import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APIClient

from spadeapp.files.models import File, FileFormat, FileProcessor, FileUpload
from spadeapp.files.service import FileService
from spadeapp.users.tests.factories import UserFactory

EXAMPLE_PROCESSOR = "spadeapp.examples.processor.ExampleFileProcessor"


@pytest.fixture
def user(db):
    user = UserFactory()
    # Explicitly demoted so ACCOUNT_FIRST_USER_ADMIN cannot promote it.
    user.is_superuser = False
    user.is_staff = False
    user.save()
    return user


@pytest.fixture
def file(db):
    fmt = FileFormat.objects.create(format="csv")
    processor = FileProcessor.objects.create(name="processor", callable=EXAMPLE_PROCESSOR)
    return File.objects.create(code="file", format=fmt, processor=processor)


@pytest.fixture
def client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


class TestUpload:
    def _url(self, file):
        return f"/api/v1/files/{file.id}/upload"

    def test_missing_file(self, client, file):
        resp = client.post(self._url(file), {"filename": "u.csv"}, format="multipart")

        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert not FileUpload.objects.exists()

    def test_missing_filename(self, client, file):
        resp = client.post(self._url(file), {"file": SimpleUploadedFile("u.csv", b"a\n1\n")}, format="multipart")

        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert not FileUpload.objects.exists()

    def test_filename_as_query_param(self, client, file):
        resp = client.post(
            f"{self._url(file)}?filename=q.csv",
            {"file": SimpleUploadedFile("u.csv", b"a\n1\n")},
            format="multipart",
        )

        assert resp.status_code == status.HTTP_200_OK, resp.content[:300]
        assert resp.json()["name"] == "q.csv"

    def test_invalid_params(self, client, file):
        resp = client.post(
            self._url(file),
            {"filename": "u.csv", "file": SimpleUploadedFile("u.csv", b"a\n1\n"), "params": "{nope"},
            format="multipart",
        )

        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert resp.json()["error_message"] == "Failed to parse user params as JSON"


def test_process_file_accepts_object_params(user, file):
    upload = FileService.process_file(file, b"a\n1\n", "u.csv", user, {"a": 1})

    assert upload.result == FileUpload.Results.SUCCESS
    assert upload.error_message is None
