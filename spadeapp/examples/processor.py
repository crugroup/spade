from spadesdk.file_processor import File, FileProcessor, FileUpload


class ExampleFileProcessor(FileProcessor):
    @classmethod
    def process(cls, file: File, filename: str, data, user_params: dict | None) -> FileUpload:
        """Process a file using the file processor."""

        return FileUpload(file=file, result=FileUpload.Result.SUCCESS, rows=1, output={"example": "output"})
