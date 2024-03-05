import logging

from spadesdk.executor import Executor, Process, RunResult

logger = logging.getLogger(__name__)


class ExampleExecutor(Executor):
    @classmethod
    def run(cls, process: "Process", user_params: dict, user_id: int) -> RunResult:
        """Execute a process using the executor."""

        logger.info("Running example executor for process %s", process.code)
        return RunResult(
            process=process, status=RunResult.Status.FINISHED, result=RunResult.Result.SUCCESS, output={"foo": "bar"}
        )
