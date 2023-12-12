from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from taggit.managers import TaggableManager

from spadeapp.processes import models as process_models


class FileFormat(models.Model):
    format = models.CharField(max_length=30, unique=True)


class FileProcessor(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
    callable = models.CharField(max_length=512, unique=True)


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

    def __str__(self):
        return self.code

    class Meta:
        ordering = ("-pk",)


class FileUpload(models.Model):
    class Results(models.TextChoices):
        SUCCESS = "success", _("Success")
        WARNING = "warning", _("Warning")
        FAILED = "failed", _("Failed")

    file = models.ForeignKey(File, on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
    result = models.CharField(max_length=20, choices=Results.choices, null=True)
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
