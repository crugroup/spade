import json
import logging
import typing

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db.models import OuterRef, Subquery
from spadesdk.executor import Executor
from spadesdk.executor import Process as SDKProcess
from spadesdk.executor import RunResult as SDKRunResult
from spadesdk.history_provider import HistoryProvider
from spadesdk.user import User as SDKUser

from ..utils.imports import import_object
from ..variables.service import VariableService
from .models import Process, ProcessRun

logger = logging.getLogger(__name__)
User = get_user_model()


class ProcessService:
    @staticmethod
    def _get_history_cache_key(process: Process, request) -> str | None:
        if request is None:
            return None

        user_id = getattr(getattr(request, "user", None), "id", "anon")
        query_string = request.GET.urlencode() if hasattr(request, "GET") else ""
        return ":".join(
            [
                "process-runs",
                str(process.id),
                str(user_id),
                process.executor.history_provider_callable or "local",
                query_string,
            ]
        )

    @staticmethod
    def _get_latest_runs_cache_key(process_ids: list[int], request) -> str | None:
        if not process_ids:
            return None

        user_id = getattr(getattr(request, "user", None), "id", "anon")
        return ":".join(["latest-process-runs", str(user_id), ",".join(map(str, sorted(process_ids)))])

    @staticmethod
    def get_latest_runs_for_processes(processes: list[Process], request) -> dict[int, ProcessRun]:
        """Get the latest run for each process with a batched local-query path."""

        cache_timeout = getattr(settings, "SPADE_LATEST_RUNS_CACHE_TIMEOUT", 60)
        process_ids = [process.id for process in processes]
        cache_key = ProcessService._get_latest_runs_cache_key(process_ids, request)
        if cache_key and cache_timeout > 0:
            cached_payload = cache.get(cache_key)
            if cached_payload is not None:
                user_ids = {run["user_id"] for run in cached_payload.values() if run.get("user_id")}
                users_by_id = User.objects.in_bulk(user_ids)
                return {
                    int(process_id): ProcessRun(
                        process=next(process for process in processes if process.id == int(process_id)),
                        status=run["status"],
                        result=run["result"],
                        output=run["output"],
                        error_message=run["error_message"],
                        created_at=run["created_at"],
                        user=users_by_id.get(run.get("user_id")),
                    )
                    for process_id, run in cached_payload.items()
                }

        latest_runs_by_process_id: dict[int, ProcessRun] = {}
        local_process_ids = [process.id for process in processes if not process.executor.history_provider_callable]

        if local_process_ids:
            latest_run_subquery = ProcessRun.objects.filter(process_id=OuterRef("pk")).order_by("-pk").values("pk")[:1]
            process_latest_run_pairs = (
                Process.objects.filter(pk__in=local_process_ids)
                .annotate(latest_run_id=Subquery(latest_run_subquery))
                .values_list("pk", "latest_run_id")
            )
            latest_run_ids_by_process_id = {
                process_id: latest_run_id
                for process_id, latest_run_id in process_latest_run_pairs
                if latest_run_id is not None
            }
            latest_runs = ProcessRun.objects.filter(pk__in=latest_run_ids_by_process_id.values()).select_related(
                "process",
                "user",
            )
            runs_by_id = {run.id: run for run in latest_runs}
            latest_runs_by_process_id.update(
                {
                    process_id: runs_by_id[latest_run_id]
                    for process_id, latest_run_id in latest_run_ids_by_process_id.items()
                    if latest_run_id in runs_by_id
                }
            )

        provider_processes = [process for process in processes if process.executor.history_provider_callable]
        for process in provider_processes:
            latest_run = next(iter(ProcessService.get_runs(process, request)), None)
            if latest_run is not None:
                latest_runs_by_process_id[process.id] = latest_run

        if cache_key and cache_timeout > 0:
            cache.set(
                cache_key,
                {
                    process_id: {
                        "status": run.status,
                        "result": run.result,
                        "output": run.output,
                        "error_message": run.error_message,
                        "created_at": run.created_at,
                        "user_id": getattr(run, "user_id", None),
                    }
                    for process_id, run in latest_runs_by_process_id.items()
                },
                cache_timeout,
            )

        return latest_runs_by_process_id

    @staticmethod
    def run_process(process: Process, user, user_params: str) -> ProcessRun:
        """Run a process using the executor."""

        logger.info(f"Running process {process} with executor {process.executor.callable}")
        executor: Executor
        if (object_key := process.executor.callable) not in settings.SPADE_PROCESS_EXECUTORS:
            executor = import_object(object_key)
            settings.SPADE_PROCESS_EXECUTORS[object_key] = executor
        else:
            executor = settings.SPADE_PROCESS_EXECUTORS[object_key]

        run: ProcessRun = ProcessRun.objects.create(
            process=process,
            user=user,
            status=ProcessRun.Statuses.RUNNING,
            user_params=user_params,
            system_params=process.system_params,
        )

        try:
            if isinstance(user_params, str):
                parsed_user_params = json.loads(user_params) if user_params else {}
            elif user_params is None:
                parsed_user_params = {}
            elif isinstance(user_params, dict):
                parsed_user_params = user_params
            else:
                raise TypeError("params must be a JSON string or object")
        except (json.JSONDecodeError, TypeError):
            run.result = ProcessRun.Results.FAILED
            run.error_message = "Failed to parse user params as JSON"
            run.status = ProcessRun.Statuses.ERROR
            run.save()
            return run

        try:
            # Get variables for the process and merge with system params
            variables = VariableService.get_variables_for_process_instance(process)
            enhanced_system_params = VariableService.merge_variables(process.system_params or {}, variables)

            logger.info(f"Process {process.code} running with {len(variables)} variables")

            result: SDKRunResult = executor.run(
                SDKProcess(
                    code=process.code,
                    system_params=enhanced_system_params,
                ),
                parsed_user_params,
                user=SDKUser(
                    id=user.id,
                    email=user.email,
                    first_name=user.first_name,
                    last_name=user.last_name,
                ),
            )
            run.result = result.result.value if result.result else None
            run.output = result.output
            run.error_message = result.error_message
            run.status = result.status.value
            run.save()
        except Exception as e:
            logger.exception(f"Error running process {process}")
            run.status = ProcessRun.Statuses.ERROR
            run.result = ProcessRun.Results.FAILED
            run.error_message = str(e)
            run.save()

        return run

    @staticmethod
    def get_runs(process: Process, request, *args, **kwargs) -> typing.Iterable[ProcessRun]:
        """Get the runs for a process."""

        if not process.executor.history_provider_callable:
            return ProcessRun.objects.filter(process=process).order_by("-pk")

        history_provider: HistoryProvider
        if (object_key := process.executor.history_provider_callable) not in settings.SPADE_HISTORY_PROVIDERS:
            try:
                history_provider = import_object(object_key)
                settings.SPADE_HISTORY_PROVIDERS[object_key] = history_provider
            except (ImportError, AttributeError):
                logger.exception(
                    "Failed to import history provider %s for process %s. Falling back to local ProcessRun records.",
                    object_key,
                    process.code,
                )
                return ProcessRun.objects.filter(process=process).order_by("-pk")
        else:
            history_provider = settings.SPADE_HISTORY_PROVIDERS[object_key]

        # Get variables for the process and merge with system params
        variables = VariableService.get_variables_for_process_instance(process)
        enhanced_system_params = VariableService.merge_variables(process.system_params or {}, variables)

        cache_timeout = getattr(settings, "SPADE_HISTORY_PROVIDER_CACHE_TIMEOUT", 60)
        cache_key = ProcessService._get_history_cache_key(process, request)
        cached_runs = cache.get(cache_key) if cache_key and cache_timeout > 0 else None

        if cached_runs is None:
            provider_results = history_provider.get_runs(
                SDKProcess(
                    code=process.code,
                    system_params=enhanced_system_params,
                ),
                request,
                *args,
                **kwargs,
            )
            cached_runs = [
                {
                    "status": result.status.value,
                    "result": result.result.value if result.result else None,
                    "output": result.output,
                    "error_message": result.error_message,
                    "created_at": result.created_at,
                    "user_id": result.user_id,
                }
                for result in provider_results
            ]
            if cache_key and cache_timeout > 0:
                cache.set(cache_key, cached_runs, cache_timeout)

        user_ids = {run["user_id"] for run in cached_runs if run.get("user_id")}
        users_by_id = User.objects.in_bulk(user_ids)
        return [
            ProcessRun(
                process=process,
                status=run["status"],
                result=run["result"],
                output=run["output"],
                error_message=run["error_message"],
                created_at=run["created_at"],
                user=users_by_id.get(run.get("user_id")),
            )
            for run in cached_runs
        ]
