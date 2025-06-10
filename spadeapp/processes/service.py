import json
import logging
import typing

from django.conf import settings
from django.contrib.auth import get_user_model
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
            parsed_user_params = json.loads(user_params) if user_params else {}
        except json.JSONDecodeError:
            run.result = ProcessRun.Results.FAILED
            run.error_message = "Failed to parse user params as JSON"
            run.save()
            return run

        try:
            # Get variables for the process and merge with system params
            variables = VariableService.get_variables_for_process(process.id)
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
            run.status = ProcessRun.Statuses.FINISHED
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
            history_provider = import_object(object_key)
            settings.SPADE_HISTORY_PROVIDERS[object_key] = history_provider
        else:
            history_provider = settings.SPADE_HISTORY_PROVIDERS[object_key]

        provider_results = history_provider.get_runs(process, request, *args, **kwargs)
        return (
            ProcessRun(
                process=process,
                status=result.status.value,
                result=result.result.value if result.result else None,
                output=result.output,
                error_message=result.error_message,
                created_at=result.created_at,
                user=User.objects.get(id=result.user_id) if result.user_id else None,
            )
            for result in provider_results
        )
