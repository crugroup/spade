from spadeapp.processes.history_provider import HistoryProvider
from spadeapp.processes.models import Process, ProcessRun


class ExampleHistoryProvider(HistoryProvider):
    @staticmethod
    def get_runs(process: Process, request, *args, **kwargs):
        return (
            ProcessRun(
                process=process,
                result=ProcessRun.Results.SUCCESS,
                status=ProcessRun.Statuses.FINISHED,
                output={"foo": "bar"},
            ),
            ProcessRun(
                process=process,
                result=ProcessRun.Results.FAILED,
                status=ProcessRun.Statuses.FINISHED,
                output={"foo": "bar"},
                error_message="Something went wrong",
            ),
        )
