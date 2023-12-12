import dataclasses


@dataclasses.dataclass
class RunResult:
    result: str
    error_message: str | None = None
    output: dict | None = None

    def __post_init__(self):
        if self.result not in ("success", "warning", "failed"):
            raise ValueError("result must be one of 'success', 'warning', or 'failed'")


class Executor:
    @staticmethod
    def run(system_params, user_params) -> RunResult:
        """Execute a process using the executor."""

        return RunResult(result="success")
