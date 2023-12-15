from django.conf import settings

from ..utils.imports import import_object
from .executor import Executor
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
