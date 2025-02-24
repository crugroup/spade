import json
import logging

from django.conf import settings
from spadesdk.file_processor import File as SDKFile
from spadesdk.file_processor import FileProcessor
from spadesdk.file_processor import FileUpload as SDKFileUpload
from spadesdk.user import User as SDKUser

from ..processes.service import ProcessService
from ..utils.imports import import_object
from .models import File, FileUpload

logger = logging.getLogger(__name__)


class FileService:
    @staticmethod
    def process_file(file: File, data, filename, user, user_params: str) -> FileUpload:
        """Process a file using the file processor."""

        logger.info(f"Uploading to file {file} with processor {file.processor.callable}")
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
            parsed_user_params = json.loads(user_params) if user_params else {}
        except json.JSONDecodeError:
            upload.result = FileUpload.Results.FAILED
            upload.error_message = "Failed to parse user params as JSON"
            upload.save()
            return upload

        try:
            result: SDKFileUpload = processor.process(
                SDKFile(
                    name=filename,
                    format=file.format.format,
                    system_params=file.system_params,
                ),
                filename=filename,
                data=data,
                user_params=parsed_user_params,
                user=SDKUser(
                    id=user.id,
                    email=user.email,
                    first_name=user.first_name,
                    last_name=user.last_name,
                ),
            )
            upload.result = result.result.value if result.result else None
            upload.rows = result.rows
            upload.output = result.output
            upload.error_message = result.error_message
            upload.save()
            if file.linked_process and upload.result == FileUpload.Results.SUCCESS:
                logger.info("Running linked process")
                try:
                    upload.linked_process_run = ProcessService.run_process(file.linked_process, user, user_params)
                except Exception:
                    logger.exception(f"Error running linked process {file.linked_process}")
                    pass
            upload.save()
        except Exception as e:
            logger.exception(f"Error processing file {file}")
            upload.result = FileUpload.Results.FAILED
            upload.error_message = str(e)
            upload.save()

        return upload
