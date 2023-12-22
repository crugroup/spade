from spadeapp.files.processor import FileProcessor, FileResult


class ExampleFileProcessor(FileProcessor):
    @staticmethod
    def process(filename, data, system_params, user_params):
        """Process a file using the file processor."""

        return FileResult(result="success")
