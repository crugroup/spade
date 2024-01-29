import logging

from spadesdk.executor import Executor, Process, RunResult

logger = logging.getLogger(__name__)


class ExampleExecutor(Executor):
    @classmethod
    def run(cls, process: "Process", user_params) -> RunResult:
        """Execute a process using the executor."""

        logger.info("Running example executor for process %s", process.code)
        return RunResult(process=process, status="finished", result="success", output={"foo": "bar"})
