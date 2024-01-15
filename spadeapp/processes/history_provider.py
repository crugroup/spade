import typing

if typing.TYPE_CHECKING:
    from .models import Process, ProcessRun


class HistoryProvider:
    @classmethod
    def get_runs(cls, process: "Process", request, *args, **kwargs) -> typing.Iterable["ProcessRun"]:
        raise NotImplementedError()
