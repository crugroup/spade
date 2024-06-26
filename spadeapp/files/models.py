from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from rules.contrib.models import RulesModel
from spadesdk.file_processor import FileProcessor as SDKFileProcessor
from taggit.managers import TaggableManager

from spadeapp.processes import models as process_models

from ..utils.imports import import_object
from ..utils.rules import defer_rule


class FileFormat(RulesModel):
    format = models.CharField(max_length=30, unique=True)

    class Meta:
        ordering = ("-pk",)
        rules_permissions = {
            "add": defer_rule("files.add_fileformat"),
            "view": defer_rule("files.view_fileformat"),
            "list": defer_rule("files.list_fileformat"),
            "change": defer_rule("files.change_fileformat"),
            "delete": defer_rule("files.delete_fileformat"),
        }

    def __str__(self):
        return self.format


class FileProcessor(RulesModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
    callable = models.CharField(max_length=512, unique=True)

    class Meta:
        ordering = ("-pk",)
        rules_permissions = {
            "view": defer_rule("files.view_fileprocessor"),
            "add": defer_rule("files.add_fileprocessor"),
            "change": defer_rule("files.change_fileprocessor"),
            "delete": defer_rule("files.delete_fileprocessor"),
        }

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


class File(RulesModel):
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
        rules_permissions = {
            "add": defer_rule("files.add_file"),
            "view": defer_rule("files.view_file"),
            "list": defer_rule("files.list_file"),
            "change": defer_rule("files.change_file"),
            "delete": defer_rule("files.delete_file"),
            "upload": defer_rule("files.upload_file"),
        }

    def __str__(self):
        return self.code


class FileUpload(RulesModel):
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
        rules_permissions = {
            "add": defer_rule("files.add_fileupload"),
            "view": defer_rule("files.view_fileupload"),
            "list": defer_rule("files.list_fileupload"),
            "change": defer_rule("files.change_fileupload"),
            "delete": defer_rule("files.delete_fileupload"),
        }

    def __str__(self):
        return f"{self.file.code} - {self.created_at}"
