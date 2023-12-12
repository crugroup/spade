from django.conf import settings

from ..utils.imports import import_object
from .executor import Executor
from .models import Process, ProcessRun


class ProcessService:
    @staticmethod
    def run_process(process: Process, user):
        """Run a process using the executor."""

        if object_key := process.executor.callable not in settings.PROCESS_EXECUTORS:
            executor = import_object(object_key)
            settings.SPADE_PROCESS_EXECUTORS[object_key] = executor
        else:
            executor: Executor = settings.SPADE_PROCESS_EXECUTORS[object_key]

        run = ProcessRun.objects.create(
            process=process,
            user=user,
            status=ProcessRun.Statuses.RUNNING,
        )

        try:
            result = executor.run(process.system_params, process.user_params)
            run.update(
                result=result.result,
                output=result.output,
                error_message=result.error_message,
            )
            return run
        except Exception as e:
            run.update(
                result=ProcessRun.Results.FAILED,
                error_message=str(e),
            )
            return run
