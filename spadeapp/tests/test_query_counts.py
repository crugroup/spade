import pytest
from django.contrib.auth.models import Group, Permission
from django.db import connection
from django.test.utils import CaptureQueriesContext
from rest_framework import status
from rest_framework.test import APIClient

from spadeapp.files.models import File, FileFormat, FileProcessor, FileUpload
from spadeapp.processes.models import Executor, Process, ProcessRun
from spadeapp.users.tests.factories import UserFactory
from spadeapp.variables.models import Variable, VariableSet

EXAMPLE_EXECUTOR = "spadeapp.examples.executor.ExampleExecutor"
EXAMPLE_PROCESSOR = "spadeapp.examples.processor.ExampleFileProcessor"


def _count_queries(client, url):
    with CaptureQueriesContext(connection) as ctx:
        resp = client.get(url)
    assert resp.status_code == status.HTTP_200_OK, resp.content[:300]
    return len(ctx.captured_queries)


def _assert_constant(client, url, add_rows):
    add_rows(0, 1)
    client.get(url)  # warm up per-process caches (e.g. ContentType) so only the view is measured
    few = _count_queries(client, url)
    add_rows(1, 5)
    many = _count_queries(client, url)
    assert many == few, f"{url}: {few} queries with few rows, {many} with many"


@pytest.fixture
def admin_user(db):
    user = UserFactory()
    user.is_superuser = True
    user.is_staff = True
    user.save()
    return user


@pytest.fixture
def api_client(admin_user):
    client = APIClient()
    client.force_authenticate(user=admin_user)
    return client


def test_existing_user_save_takes_one_query(admin_user, django_assert_num_queries):
    with django_assert_num_queries(1):
        admin_user.save()


def test_user_list_query_count(api_client):
    group = Group.objects.create(name="group")
    permission = Permission.objects.first()

    def add_rows(start, stop):
        for _ in range(start, stop):
            user = UserFactory()
            user.groups.add(group)
            user.user_permissions.add(permission)

    _assert_constant(api_client, "/api/v1/users", add_rows)


def test_group_list_query_count(api_client):
    permission = Permission.objects.first()

    def add_rows(start, stop):
        for i in range(start, stop):
            Group.objects.create(name=f"group-{i}").permissions.add(permission)

    _assert_constant(api_client, "/api/v1/groups", add_rows)


@pytest.fixture
def history(db, admin_user):
    executor = Executor.objects.create(name="executor", callable=EXAMPLE_EXECUTOR)
    fmt = FileFormat.objects.create(format="csv")
    processor = FileProcessor.objects.create(name="processor", callable=EXAMPLE_PROCESSOR)

    def add_rows(start, stop):
        for i in range(start, stop):
            process = Process.objects.create(code=f"process-{i}", executor=executor)
            ProcessRun.objects.create(process=process, user=admin_user)
            file = File.objects.create(code=f"file-{i}", format=fmt, processor=processor)
            FileUpload.objects.create(file=file, user=admin_user, name=f"u{i}.csv")
            variable_set = VariableSet.objects.create(name=f"set-{i}")
            variable_set.variables.add(Variable.objects.create(name=f"var-{i}", value="v"))

    return add_rows


@pytest.mark.parametrize(
    "model_url",
    [
        "processes/process",
        "processes/processrun",
        "files/file",
        "files/fileupload",
        "variables/variableset",
    ],
)
def test_admin_changelist_query_count(client, admin_user, history, model_url):
    client.force_login(admin_user)

    _assert_constant(client, f"/admin/{model_url}/", history)
