from django.conf import settings
from spadesdk.file_processor import File as SDKFile
from spadesdk.file_processor import FileProcessor
from spadesdk.file_processor import FileUpload as SDKFileUpload

from ..utils.imports import import_object
from .models import File, FileUpload


class FileService:
    @staticmethod
    def process_file(file: File, data, filename, user, user_params: dict) -> FileUpload:
        """Process a file using the file processor."""

        processor: FileProcessor
        if (object_key := file.processor.callable) not in settings.SPADE_FILE_PROCESSORS:
            processor = import_object(object_key)
            settings.SPADE_FILE_PROCESSORS[object_key] = processor
        else:
            processor = settings.SPADE_FILE_PROCESSORS[object_key]

        upload: FileUpload = FileUpload.objects.create(
            file=file,
            name=filename,
            user=user,
            size=len(data),
            user_params=user_params,
        )

        try:
            result: SDKFileUpload = processor.process(
                SDKFile(
                    name=filename,
                    format=file.format.format,
                    system_params=file.system_params,
                ),
                filename=filename,
                data=data,
                user_params=user_params,
            )
            upload.result = result.result
            upload.rows = result.rows
            upload.output = result.output
            upload.error_message = result.error_message
            upload.save()
        except Exception as e:
            upload.result = FileUpload.Results.FAILED
            upload.error_message = str(e)
            upload.save()

        return upload
