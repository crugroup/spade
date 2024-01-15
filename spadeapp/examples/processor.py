from spadeapp.files.processor import FileProcessor, FileResult


class ExampleFileProcessor(FileProcessor):
    @classmethod
    def process(cls, filename, data, system_params, user_params):
        """Process a file using the file processor."""

        return FileResult(result="success")
