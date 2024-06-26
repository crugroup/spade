from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from spadesdk.file_processor import FileProcessor as SDKFileProcessor
from taggit.managers import TaggableManager

from spadeapp.processes import models as process_models

from ..utils.imports import import_object


class FileFormat(models.Model):
    format = models.CharField(max_length=30, unique=True)

    class Meta:
        ordering = ("-pk",)

    def __str__(self):
        return self.format


class FileProcessor(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
    callable = models.CharField(max_length=512, unique=True)

    class Meta:
        ordering = ("-pk",)

    def __str__(self):
        return self.name

    def clean(self):
        self.validate(self.callable)

    @staticmethod
    def validate(callable_value: str, exception_class=ValidationError):
        if "." not in callable_value:
            raise exception_class(f"`{callable_value}` must be a fully qualified python path")

        try:
            processor_callable = import_object(callable_value)
        except (ImportError, AttributeError):
            raise exception_class(f"`{callable_value}` could not be imported")

        if not isinstance(processor_callable, type) or not issubclass(processor_callable, SDKFileProcessor):
            raise exception_class(f"`{callable_value}` is not a subclass of spadesdk.file_processor.FileProcessor")


class File(models.Model):
    code = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
    tags = TaggableManager(blank=True)
    format = models.ForeignKey(FileFormat, on_delete=models.CASCADE)
    processor = models.ForeignKey(FileProcessor, on_delete=models.CASCADE)
    system_params = models.JSONField(null=True, blank=True)
    user_params = models.JSONField(null=True, blank=True)
    linked_process = models.ForeignKey(process_models.Process, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-pk",)

    def __str__(self):
        return self.code


class FileUpload(models.Model):
    class Results(models.TextChoices):
        SUCCESS = "success", _("Success")
        WARNING = "warning", _("Warning")
        FAILED = "failed", _("Failed")

    file = models.ForeignKey(File, on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
    result = models.CharField(max_length=20, choices=Results, null=True)
    system_params = models.JSONField(null=True, blank=True)
    user_params = models.JSONField(null=True, blank=True)
    output = models.JSONField(null=True, blank=True)
    size = models.IntegerField(default=0)
    rows = models.IntegerField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    linked_process_run = models.OneToOneField(
        process_models.ProcessRun, on_delete=models.SET_NULL, null=True, blank=True
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-pk",)

    def __str__(self):
        return f"{self.file.code} - {self.created_at}"
