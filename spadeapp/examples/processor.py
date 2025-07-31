import logging

from spadesdk.file_processor import File, FileProcessor, FileUpload
from spadesdk.user import User

logger = logging.getLogger(__name__)


class ExampleFileProcessor(FileProcessor):
    @classmethod
    def process(
        cls, file: File, filename: str, data, user_params: dict | None, user: User, *args, **kwargs
    ) -> FileUpload:
        """Process a file using the file processor."""
        logger.info("Running example executor for process %s", file.name)
        logger.info("System parameters: %s", file.system_params)
        logger.info("User parameters: %s", user_params)

        return FileUpload(file=file, result=FileUpload.Result.SUCCESS, rows=1, output={"example": "output"})
