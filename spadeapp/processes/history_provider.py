import typing

if typing.TYPE_CHECKING:
    from .models import Process, ProcessRun


class HistoryProvider:
    @staticmethod
    def get_runs(process: "Process", request, *args, **kwargs) -> typing.Iterable["ProcessRun"]:
        raise NotImplementedError()
