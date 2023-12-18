from django.conf import settings

from ..utils.imports import import_object
from .executor import Executor
from .history_provider import HistoryProvider
from .models import Process, ProcessRun


class ProcessService:
    @staticmethod
    def run_process(process: Process, user, user_params: dict) -> ProcessRun:
        """Run a process using the executor."""

        if (object_key := process.executor.callable) not in settings.SPADE_PROCESS_EXECUTORS:
            executor = import_object(object_key)
            settings.SPADE_PROCESS_EXECUTORS[object_key] = executor
        else:
            executor: Executor = settings.SPADE_PROCESS_EXECUTORS[object_key]

        run: ProcessRun = ProcessRun.objects.create(
            process=process,
            user=user,
            status=ProcessRun.Statuses.RUNNING,
            user_params=user_params,
        )

        try:
            result = executor.run(process.system_params, user_params)
            run.result = result.result
            run.output = result.output
            run.error_message = result.error_message
            run.status = ProcessRun.Statuses.FINISHED
            run.save()
        except Exception as e:
            run.status = ProcessRun.Statuses.ERROR
            run.result = ProcessRun.Results.FAILED
            run.error_message = str(e)
            run.save()

        return run

    @staticmethod
    def get_runs(process: Process, request, *args, **kwargs):
        """Get the runs for a process."""

        if not process.executor.history_provider_callable:
            return ProcessRun.objects.filter(process=process).order_by("-pk")

        if (object_key := process.executor.history_provider_callable) not in settings.SPADE_HISTORY_PROVIDERS:
            history_provider = import_object(object_key)
            settings.SPADE_HISTORY_PROVIDERS[object_key] = history_provider
        else:
            history_provider: HistoryProvider = settings.SPADE_HISTORY_PROVIDERS[object_key]

        return history_provider.get_runs(process, request, *args, **kwargs)
