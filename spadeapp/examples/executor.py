import logging

from spadeapp.processes.executor import Executor, RunResult

logger = logging.getLogger(__name__)


class ExampleExecutor(Executor):
    @classmethod
    def run(cls, system_params, user_params) -> RunResult:
        """Execute a process using the executor."""

        logger.info("Running example executor")
        return RunResult(result="success")
