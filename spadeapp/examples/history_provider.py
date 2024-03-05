from spadesdk.history_provider import HistoryProvider, Process, RunResult


class ExampleHistoryProvider(HistoryProvider):
    @classmethod
    def get_runs(cls, process: Process, request, *args, **kwargs):
        return (
            RunResult(
                process=process,
                result=RunResult.Result.SUCCESS,
                status=RunResult.Status.FINISHED,
                output={"foo": "bar"},
            ),
            RunResult(
                process=process,
                result=RunResult.Result.FAILED,
                status=RunResult.Status.FINISHED,
                output={"foo": "bar"},
                error_message="Something went wrong",
            ),
        )
