import pytest
import rules
from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APIClient

from spadeapp.processes.models import Executor, Process, ProcessRun
from spadeapp.users.tests.factories import UserFactory
from spadeapp.utils.permissions import SpadePermissionManager, permission_manager_cache

EXAMPLE_EXECUTOR = "spadeapp.examples.executor.ExampleExecutor"


@pytest.fixture(autouse=True)
def _clear_cache():
    cache.clear()
    yield
    cache.clear()


def _normal_user():
    user = UserFactory()
    # Explicitly demoted so ACCOUNT_FIRST_USER_ADMIN cannot promote it.
    user.is_superuser = False
    user.is_staff = False
    user.save()
    return user


@pytest.fixture
def user(db):
    return _normal_user()


@pytest.fixture
def process(db):
    executor = Executor.objects.create(name="executor", callable=EXAMPLE_EXECUTOR)
    return Process.objects.create(code="process", executor=executor, system_params={"region": "EU"})


@pytest.fixture
def client_for():
    def make(user):
        client = APIClient()
        client.force_authenticate(user=user)
        return client

    return make


class TestRun:
    def test_run_without_params(self, client_for, user, process):
        resp = client_for(user).post(f"/api/v1/processes/{process.id}/run", {}, format="json")

        assert resp.status_code == status.HTTP_200_OK, resp.content[:300]
        assert resp.json()["status"] == ProcessRun.Statuses.FINISHED

    def test_run_with_object_params(self, client_for, user, process):
        resp = client_for(user).post(f"/api/v1/processes/{process.id}/run", {"params": {"a": 1}}, format="json")

        assert resp.status_code == status.HTTP_200_OK, resp.content[:300]

    def test_run_with_invalid_params(self, client_for, user, process):
        resp = client_for(user).post(f"/api/v1/processes/{process.id}/run", {"params": "{nope"}, format="json")

        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert resp.json()["error_message"] == "Failed to parse user params as JSON"


class TestRunsList:
    def test_non_integer_process_filter(self, client_for, user, process):
        resp = client_for(user).get("/api/v1/processruns?process=abc")

        assert resp.status_code == status.HTTP_400_BAD_REQUEST


class TestLatestRunsCache:
    def _latest(self, client, process):
        resp = client.get(f"/api/v1/processes/latest_runs?ids={process.id}")
        assert resp.status_code == status.HTTP_200_OK, resp.content[:300]
        return resp.json()

    def test_cache_hit_matches_miss(self, client_for, user, process):
        client = client_for(user)
        client.post(f"/api/v1/processes/{process.id}/run", {"params": '{"a": 1}'}, format="json")

        miss = self._latest(client, process)
        hit = self._latest(client, process)

        assert miss[0]["latest_run"]["id"] is not None
        assert miss[0]["latest_run"]["user_params"] == '{"a": 1}'
        assert miss[0]["latest_run"]["system_params"] == {"region": "EU"}
        assert hit == miss

    def test_run_invalidates_other_users_cache(self, client_for, user, process):
        other_client = client_for(_normal_user())
        assert self._latest(other_client, process) == [{"process_id": process.id, "latest_run": None}]

        client_for(user).post(f"/api/v1/processes/{process.id}/run", {"params": "{}"}, format="json")

        latest_run = self._latest(other_client, process)[0]["latest_run"]
        assert latest_run is not None
        assert latest_run["id"] == ProcessRun.objects.get(process=process).id


@rules.predicate
def run_not_hidden(user, run):
    return run is None or run.error_message != "hidden"


class HideMarkedRunsPermissionManager(SpadePermissionManager):
    def __init__(self):
        super().__init__()
        self.add_rule("processes.view_processrun", run_not_hidden)


class TestLatestRunsRunPermission:
    @pytest.fixture(autouse=True)
    def _hide_marked_runs(self, settings):
        settings.SPADE_PERMISSION_MANAGER = f"{__name__}.HideMarkedRunsPermissionManager"
        permission_manager_cache.cache.clear()
        yield
        permission_manager_cache.cache.clear()

    def test_hidden_latest_run_not_returned(self, client_for, user, process):
        ProcessRun.objects.create(process=process, user=user, error_message="hidden")
        client = client_for(user)

        miss = client.get(f"/api/v1/processes/latest_runs?ids={process.id}").json()
        hit = client.get(f"/api/v1/processes/latest_runs?ids={process.id}").json()

        assert miss == [{"process_id": process.id, "latest_run": None}]
        assert hit == miss

    def test_visible_latest_run_returned(self, client_for, user, process):
        run = ProcessRun.objects.create(process=process, user=user, error_message="shown")

        latest = client_for(user).get(f"/api/v1/processes/latest_runs?ids={process.id}").json()

        assert latest[0]["latest_run"]["id"] == run.id
