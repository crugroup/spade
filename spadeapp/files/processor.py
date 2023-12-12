import dataclasses


@dataclasses.dataclass
class FileResult:
    result: str
    rows: int | None = None
    error_message: str | None = None
    output: dict | None = None

    def __post_init__(self):
        if self.result not in ("success", "warning", "failed"):
            raise ValueError("result must be one of 'success', 'warning', or 'failed'")


class FileProcessor:
    @staticmethod
    def process(filename, data, system_params, user_params) -> FileResult:
        """Process a file using the file processor."""

        return FileResult(result="success")
