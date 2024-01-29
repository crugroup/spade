from spadesdk.history_provider import HistoryProvider, Process, RunResult


class ExampleHistoryProvider(HistoryProvider):
    @classmethod
    def get_runs(cls, process: Process, request, *args, **kwargs):
        return (
            RunResult(
                process=process,
                result="success",
                status="finished",
                output={"foo": "bar"},
            ),
            RunResult(
                process=process,
                result="failed",
                status="finished",
                output={"foo": "bar"},
                error_message="Something went wrong",
            ),
        )
