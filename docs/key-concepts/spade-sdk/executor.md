---
sidebar_position: 2
---

# Executor
An **Executor** is a class designed to trigger a job in an external service, and are the backbone
of [Processes](../process.md).

The main method that defines an Executor is `run`:

```python
class Executor:
    @classmethod
    def run(cls, process: Process, user_params: dict, user: User, *args, **kwargs) -> RunResult:
        pass
```

The method is used as a class method, and should not store anything that isn't required
for every use of this executor (these should go in [parameters](../parameters.md) instead).

When a run is triggered, this method is called with the Process object (containing the system
parameters), the user parameters, and the ID of the Spade user who triggered the run. The
result is a RunResult object, denoting things such as if the job was successful, any output
of the action, or an error message if something went wrong.

In the case that a [History Provider](history-provider.md) is used alongside the Executor,
the result of that History Provider will override the returned RunResults of the Executor.
