from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from taggit.managers import TaggableManager


class Executor(models.Model):
    name = models.CharField(max_length=100)
    executor = models.CharField(max_length=512)
    history_provider = models.CharField(max_length=512, null=True, blank=True)


class Process(models.Model):
    code = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
    tags = TaggableManager(blank=True)
    executor = models.ForeignKey(Executor, on_delete=models.CASCADE)
    system_params = models.JSONField(null=True, blank=True)
    user_params = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code

    class Meta:
        ordering = ("-pk",)


class ProcessRun(models.Model):
    class Results(models.TextChoices):
        SUCCESS = "success", _("Success")
        WARNING = "warning", _("Warning")
        FAILED = "failed", _("Failed")

    class Statuses(models.TextChoices):
        NEW = "new", _("New")
        RUNNING = "running", _("Running")
        FINISHED = "finished", _("Finished")
        ERROR = "error", _("Error")

    process = models.ForeignKey(Process, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=Statuses.choices, default=Statuses.NEW)
    result = models.CharField(max_length=20, choices=Results.choices, null=True, blank=True)
    system_params = models.JSONField(null=True, blank=True)
    user_params = models.JSONField(null=True, blank=True)
    output = models.JSONField(null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.PROTECT)
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-pk",)
