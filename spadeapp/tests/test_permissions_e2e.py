"""
End-to-end permission tests for every API endpoint.

These guard against the class of regression where a dependency upgrade (e.g. a
Dependabot bump) breaks permission resolution for non-superusers while the
existing unit tests still pass. Concrete historical failures this suite catches:

* a missing ``rules_permissions["list"]`` entry turning a list endpoint into a
  hard 403 for every non-superuser;
* a ``.union()`` of ``Permission`` querysets crashing because ``Permission`` has
  a default ``Meta.ordering`` and UNION forbids ORDER BY in its subqueries;
* a ``GroupViewSet`` queryset with no ordering breaking pagination.

Two permission managers are exercised, mirroring the shipped example classes:

* ``SpadePermissionManager`` (the default): every rule falls back to
  ``always_allow``, so a logged-in non-superuser may read everything and run
  processes/upload files.
* ``TaggedPermissionManager``: object visibility for files/processes (view, run,
  upload) is gated on the intersection of the user's group names and the
  object's tag names. Everything else falls back to ``always_allow``.
"""

import pytest
import rules
from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APIClient

from spadeapp.files.models import File, FileFormat, FileProcessor, FileUpload
from spadeapp.processes.models import Executor, Process, ProcessRun
from spadeapp.users.tests.factories import UserFactory
from spadeapp.utils.permissions import SpadePermissionManager, permission_manager_cache
from spadeapp.variables.models import Variable, VariableSet

TAGGED_MANAGER = "spadeapp.examples.tagged_permission_manager.TaggedPermissionManager"

EXAMPLE_EXECUTOR = "spadeapp.examples.executor.ExampleExecutor"
EXAMPLE_PROCESSOR = "spadeapp.examples.processor.ExampleFileProcessor"


@pytest.fixture(autouse=True)
def _clear_permission_manager_cache():
    """Each test must rebuild the manager from the active settings."""
    permission_manager_cache.cache.clear()
    yield
    permission_manager_cache.cache.clear()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def normal_user(db):
    """A non-superuser, explicitly demoted so ACCOUNT_FIRST_USER_ADMIN cannot promote it."""
    user = UserFactory()
    user.is_superuser = False
    user.is_staff = False
    user.save()
    return user


@pytest.fixture
def admin_user(db):
    return UserFactory(is_superuser=True, is_staff=True)


@pytest.fixture
def data(db):
    """A single row of every model, wired up with the example executor/processor classes."""
    executor = Executor.objects.create(name="executor", callable=EXAMPLE_EXECUTOR)
    process = Process.objects.create(code="process", executor=executor)

    fmt = FileFormat.objects.create(format="csv")
    processor = FileProcessor.objects.create(name="processor", callable=EXAMPLE_PROCESSOR)
    file = File.objects.create(code="file", format=fmt, processor=processor)

    variable = Variable.objects.create(name="variable", value="value")
    variable_set = VariableSet.objects.create(name="variable-set")
    variable_set.variables.add(variable)

    return {
        "executor": executor,
        "process": process,
        "file_format": fmt,
        "file_processor": processor,
        "file": file,
        "variable": variable,
        "variable_set": variable_set,
    }


@pytest.fixture
def tagged_data(db):
    """
    Files/processes split across two tag namespaces. A user in group ``Sales``
    can see/run the ``Sales``-tagged objects but not the ``Finance``-tagged ones.
    """
    sales_group = Group.objects.create(name="Sales")
    finance_group = Group.objects.create(name="Finance")

    executor = Executor.objects.create(name="executor", callable=EXAMPLE_EXECUTOR)
    processor = FileProcessor.objects.create(name="processor", callable=EXAMPLE_PROCESSOR)
    fmt = FileFormat.objects.create(format="csv")

    sales_file = File.objects.create(code="sales-file", format=fmt, processor=processor)
    sales_file.tags.add("Sales")
    finance_file = File.objects.create(code="finance-file", format=fmt, processor=processor)
    finance_file.tags.add("Finance")

    sales_process = Process.objects.create(code="sales-process", executor=executor)
    sales_process.tags.add("Sales")
    finance_process = Process.objects.create(code="finance-process", executor=executor)
    finance_process.tags.add("Finance")

    return {
        "sales_group": sales_group,
        "finance_group": finance_group,
        "sales_file": sales_file,
        "finance_file": finance_file,
        "sales_process": sales_process,
        "finance_process": finance_process,
    }


READ_ENDPOINTS = [
    "users-list",
    "users-me",
    "users-me-permissions",
    "permissions-list",
    "groups-list",
    "favorites-list",
    "files-list",
    "files-detail",
    "fileformats-list",
    "fileformats-detail",
    "fileprocessors-list",
    "fileprocessors-detail",
    "fileuploads-list",
    "processes-list",
    "processes-detail",
    "processes-latest-runs",
    "processruns-list",
    "executors-list",
    "executors-detail",
    "variables-list",
    "variables-detail",
    "variable-sets-list",
    "variable-sets-detail",
    "tags-list",
]


def _urls(data):
    return {
        "users-list": "/api/v1/users",
        "users-me": "/api/v1/users/me",
        "users-me-permissions": "/api/v1/users/me/permissions",
        "permissions-list": "/api/v1/permissions",
        "groups-list": "/api/v1/groups",
        "favorites-list": "/api/v1/favorites",
        # files
        "files-list": "/api/v1/files",
        "files-detail": f"/api/v1/files/{data['file'].id}",
        "fileformats-list": "/api/v1/fileformats",
        "fileformats-detail": f"/api/v1/fileformats/{data['file_format'].id}",
        "fileprocessors-list": "/api/v1/fileprocessors",
        "fileprocessors-detail": f"/api/v1/fileprocessors/{data['file_processor'].id}",
        "fileuploads-list": "/api/v1/fileuploads",
        # processes
        "processes-list": "/api/v1/processes",
        "processes-detail": f"/api/v1/processes/{data['process'].id}",
        "processes-latest-runs": "/api/v1/processes/latest_runs",
        "processruns-list": "/api/v1/processruns",
        "executors-list": "/api/v1/executors",
        "executors-detail": f"/api/v1/executors/{data['executor'].id}",
        # variables
        "variables-list": "/api/v1/variables",
        "variables-detail": f"/api/v1/variables/{data['variable'].id}",
        "variable-sets-list": "/api/v1/variable-sets",
        "variable-sets-detail": f"/api/v1/variable-sets/{data['variable_set'].id}",
        # utils
        "tags-list": "/api/v1/tags",
    }


def _admin_url(url_key, user):
    """URLs for the admin-only user/group management endpoints."""
    return {
        "users-list": "/api/v1/users",
        "groups-list": "/api/v1/groups",
        "users-detail": f"/api/v1/users/{user.id}",
    }[url_key]


class TestAnonymousRejected:
    @pytest.mark.parametrize("endpoint", READ_ENDPOINTS)
    def test_read_requires_auth(self, api_client, data, endpoint):
        resp = api_client.get(_urls(data)[endpoint])
        assert resp.status_code in (
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        ), f"{endpoint} allowed anonymous: {resp.status_code}"


class TestDefaultManagerAllowAll:
    """With the default SpadePermissionManager every rule allows access."""

    @pytest.mark.parametrize("endpoint", READ_ENDPOINTS)
    def test_non_superuser_can_read_everything(self, db, api_client, normal_user, data, endpoint):
        api_client.force_authenticate(user=normal_user)
        resp = api_client.get(_urls(data)[endpoint])
        assert resp.status_code == status.HTTP_200_OK, f"{endpoint}: {resp.status_code} {resp.content[:300]}"

    @pytest.mark.parametrize("endpoint", READ_ENDPOINTS)
    def test_superuser_can_read_everything(self, db, api_client, admin_user, data, endpoint):
        api_client.force_authenticate(user=admin_user)
        resp = api_client.get(_urls(data)[endpoint])
        assert resp.status_code == status.HTTP_200_OK, f"{endpoint}: {resp.status_code} {resp.content[:300]}"

    def test_non_superuser_can_run_process(self, db, api_client, normal_user, data):
        api_client.force_authenticate(user=normal_user)
        resp = api_client.post(
            f"/api/v1/processes/{data['process'].id}/run",
            {"params": "{}"},
            format="json",
        )
        assert resp.status_code == status.HTTP_200_OK, f"run: {resp.status_code} {resp.content[:300]}"

    def test_non_superuser_can_upload_file(self, db, api_client, normal_user, data):
        api_client.force_authenticate(user=normal_user)
        resp = api_client.post(
            f"/api/v1/files/{data['file'].id}/upload",
            {
                "filename": "upload.csv",
                "file": SimpleUploadedFile("upload.csv", b"a,b\n1,2\n"),
            },
            format="multipart",
        )
        assert resp.status_code == status.HTTP_200_OK, f"upload: {resp.status_code} {resp.content[:300]}"


class TestAdminOnlyManagement:
    """User/Group management stays admin-only even under the allow-all manager."""

    @pytest.mark.parametrize(
        "method,url_key",
        [
            ("post", "users-list"),
            ("post", "groups-list"),
            ("patch", "users-detail"),
            ("put", "users-detail"),
            ("delete", "users-detail"),
        ],
    )
    def test_non_superuser_denied(self, api_client, normal_user, admin_user, method, url_key):
        url = _admin_url(url_key, admin_user)
        api_client.force_authenticate(user=normal_user)
        resp = getattr(api_client, method)(url)
        assert resp.status_code == status.HTTP_403_FORBIDDEN, f"{method} {url_key}: {resp.status_code}"

    @pytest.mark.parametrize(
        "method,url_key",
        [
            ("post", "users-list"),
            ("post", "groups-list"),
            ("get", "users-detail"),
            ("delete", "users-detail"),
        ],
    )
    def test_superuser_allowed(self, api_client, admin_user, method, url_key):
        url = _admin_url(url_key, admin_user)
        api_client.force_authenticate(user=admin_user)
        resp = getattr(api_client, method)(url)
        # Assert the permission gate passed (i.e. not 401/403); validation errors are fine.
        assert resp.status_code not in (
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
        ), f"{method} {url_key}: {resp.status_code}"


class TestTaggedPermissionManager:
    @pytest.fixture
    def tagged_manager(self, settings):
        settings.SPADE_PERMISSION_MANAGER = TAGGED_MANAGER
        permission_manager_cache.cache.clear()

    def _sales_user(self, db, tagged_data):
        user = UserFactory()
        user.is_superuser = False
        user.is_staff = False
        user.save()
        user.groups.add(tagged_data["sales_group"])
        return user

    def test_matching_tag_visible_in_list(self, db, api_client, tagged_data, tagged_manager):
        user = self._sales_user(db, tagged_data)
        api_client.force_authenticate(user=user)
        files = api_client.get("/api/v1/files").json()
        codes = {f["code"] for f in files}
        assert "sales-file" in codes
        assert "finance-file" not in codes

    def test_non_matching_detail_denied(self, db, api_client, tagged_data, tagged_manager):
        user = self._sales_user(db, tagged_data)
        api_client.force_authenticate(user=user)
        ok = api_client.get(f"/api/v1/files/{tagged_data['sales_file'].id}")
        denied = api_client.get(f"/api/v1/files/{tagged_data['finance_file'].id}")
        assert ok.status_code == status.HTTP_200_OK
        assert denied.status_code == status.HTTP_403_FORBIDDEN

    def test_upload_gated_on_tags(self, db, api_client, tagged_data, tagged_manager):
        user = self._sales_user(db, tagged_data)
        api_client.force_authenticate(user=user)
        ok = api_client.post(
            f"/api/v1/files/{tagged_data['sales_file'].id}/upload",
            {"filename": "u.csv", "file": SimpleUploadedFile("u.csv", b"a\n1\n")},
            format="multipart",
        )
        denied = api_client.post(
            f"/api/v1/files/{tagged_data['finance_file'].id}/upload",
            {"filename": "u.csv", "file": SimpleUploadedFile("u.csv", b"a\n1\n")},
            format="multipart",
        )
        assert ok.status_code == status.HTTP_200_OK, f"matching upload: {ok.status_code} {ok.content[:200]}"
        assert denied.status_code == status.HTTP_403_FORBIDDEN

    def test_run_gated_on_tags(self, db, api_client, tagged_data, tagged_manager):
        user = self._sales_user(db, tagged_data)
        api_client.force_authenticate(user=user)
        ok = api_client.post(
            f"/api/v1/processes/{tagged_data['sales_process'].id}/run",
            {"params": "{}"},
            format="json",
        )
        denied = api_client.post(
            f"/api/v1/processes/{tagged_data['finance_process'].id}/run",
            {"params": "{}"},
            format="json",
        )
        assert ok.status_code == status.HTTP_200_OK, f"matching run: {ok.status_code} {ok.content[:200]}"
        assert denied.status_code == status.HTTP_403_FORBIDDEN

    def test_superuser_bypasses_tags(self, db, api_client, tagged_data, tagged_manager):
        user = UserFactory(is_superuser=True, is_staff=True)
        api_client.force_authenticate(user=user)
        resp = api_client.get(f"/api/v1/files/{tagged_data['finance_file'].id}")
        assert resp.status_code == status.HTTP_200_OK

    def _history(self, tagged_data, user):
        runs = {
            key: ProcessRun.objects.create(process=tagged_data[f"{key}_process"], user=user)
            for key in ("sales", "finance")
        }
        uploads = {
            key: FileUpload.objects.create(file=tagged_data[f"{key}_file"], name="u.csv", user=user)
            for key in ("sales", "finance")
        }
        return runs, uploads

    def test_process_runs_follow_process_visibility(self, db, api_client, tagged_data, tagged_manager):
        user = self._sales_user(db, tagged_data)
        runs, _ = self._history(tagged_data, user)
        api_client.force_authenticate(user=user)

        listed = api_client.get("/api/v1/processruns").json()["results"]
        by_process = api_client.get(f"/api/v1/processruns?process={tagged_data['finance_process'].id}")
        detail = api_client.get(f"/api/v1/processruns/{runs['finance'].id}")

        assert {run["id"] for run in listed} == {runs["sales"].id}
        assert by_process.status_code == status.HTTP_200_OK
        assert by_process.json() == []
        assert detail.status_code == status.HTTP_404_NOT_FOUND

    def test_file_uploads_follow_file_visibility(self, db, api_client, tagged_data, tagged_manager):
        user = self._sales_user(db, tagged_data)
        _, uploads = self._history(tagged_data, user)
        api_client.force_authenticate(user=user)

        listed = api_client.get("/api/v1/fileuploads").json()
        detail = api_client.get(f"/api/v1/fileuploads/{uploads['finance'].id}")

        assert {upload["id"] for upload in listed} == {uploads["sales"].id}
        assert detail.status_code == status.HTTP_404_NOT_FOUND


class DenyVariablesPermissionManager(SpadePermissionManager):
    """Allows everything except the variable and variable set rules."""

    def __init__(self):
        super().__init__()
        for model in ("variable", "variableset"):
            for action in ("add", "view", "list", "change", "delete"):
                self.add_rule(f"variables.{action}_{model}", rules.always_deny)


class TestVariablesUsePermissionManager:
    @pytest.fixture
    def deny_variables_manager(self, settings):
        settings.SPADE_PERMISSION_MANAGER = f"{__name__}.DenyVariablesPermissionManager"
        permission_manager_cache.cache.clear()

    @pytest.mark.parametrize("base", ["/api/v1/variables", "/api/v1/variable-sets"])
    def test_denied_by_manager(self, api_client, normal_user, data, deny_variables_manager, base):
        detail_id = data["variable"].id if base.endswith("variables") else data["variable_set"].id
        api_client.force_authenticate(user=normal_user)

        responses = {
            "list": api_client.get(base),
            "detail": api_client.get(f"{base}/{detail_id}"),
            "create": api_client.post(base, {"name": "new", "value": "v"}, format="json"),
            "update": api_client.patch(f"{base}/{detail_id}", {"description": "changed"}, format="json"),
            "delete": api_client.delete(f"{base}/{detail_id}"),
        }

        for action, resp in responses.items():
            assert resp.status_code == status.HTTP_403_FORBIDDEN, f"{action}: {resp.status_code}"
        assert Variable.objects.filter(pk=data["variable"].pk).exists()
        assert VariableSet.objects.filter(pk=data["variable_set"].pk).exists()

    def test_superuser_still_allowed(self, api_client, admin_user, data, deny_variables_manager):
        api_client.force_authenticate(user=admin_user)

        resp = api_client.post("/api/v1/variables", {"name": "new", "value": "v"}, format="json")

        assert resp.status_code == status.HTTP_201_CREATED, resp.content[:300]
