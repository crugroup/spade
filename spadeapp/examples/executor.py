import logging

from spadesdk.executor import Executor, Process, RunResult
from spadesdk.user import User

logger = logging.getLogger(__name__)


class ExampleExecutor(Executor):
    @classmethod
    def run(cls, process: "Process", user_params: dict, user: User, *args, **kwargs) -> RunResult:
        """Execute a process using the executor."""

        logger.info("Running example executor for process %s", process.code)
        logger.info("System parameters: %s", process.system_params)
        logger.info("User parameters: %s", user_params)
        return RunResult(
            process=process, status=RunResult.Status.FINISHED, result=RunResult.Result.SUCCESS, output={"foo": "bar"}
        )
