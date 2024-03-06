---
sidebar_position: 3
---

# History Provider
A **History Provider** is a class for retrieving previous runs of an Executor, in the event
that the Executor triggers a job in another service, such as Apache Airflow.

The main method of a history provider is `get_runs`:

```python
class HistoryProvider:
    @classmethod
    def get_runs(cls, process: Process, request, *args, **kwargs) -> typing.Iterable["RunResult"]:
        pass
```

The parameters are the Process object to retrieve runs from, the Django request that triggered
the job, and any additional parameters that are (???). The return result is any iterable of
RunResults that would be returned by the Executor.

A History Provider, if assigned to a [Process](../process.md), will override the run results of the executor.