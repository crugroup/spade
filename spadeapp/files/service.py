from django.conf import settings

from ..utils.imports import import_object
from .models import File, FileUpload
from .processor import FileProcessor


class FileService:
    @staticmethod
    def process_file(file: File, data, filename, user):
        """Process a file using the file processor."""

        if object_key := file.processor.callable not in settings.FILE_PROCESSORS:
            processor = import_object(object_key)
            settings.SPADE_FILE_PROCESSORS[object_key] = processor
        else:
            processor: FileProcessor = settings.SPADE_FILE_PROCESSORS[object_key]

        upload = FileUpload.objects.create(
            file=file,
            name=filename,
            user=user,
            size=len(data),
        )

        try:
            result = processor.process(filename, data, file.system_params, file.user_params)
            upload.update(
                result=result.result,
                rows=result.rows,
                output=result.output,
                error_message=result.error_message,
            )
            return upload
        except Exception as e:
            upload.update(
                result=FileUpload.Results.FAILED,
                error_message=str(e),
            )
            return upload
