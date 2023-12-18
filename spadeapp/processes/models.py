from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from taggit.managers import TaggableManager

from ..processes.executor import Executor as BaseExecutor
from ..processes.history_provider import HistoryProvider as BaseHistoryProvider
from ..utils.imports import import_object


class Executor(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    callable = models.CharField(max_length=512)
    history_provider_callable = models.CharField(max_length=512, null=True, blank=True)

    def __str__(self):
        return self.name

    def clean(self):
        if "." not in self.callable:
            raise ValidationError(f"`{self.callable}` must be a fully qualified python path")

        try:
            executor_callable = import_object(self.callable)
        except (ImportError, AttributeError):
            raise ValidationError(f"`{self.callable}` could not be imported")

        if not isinstance(executor_callable, type) or not issubclass(executor_callable, BaseExecutor):
            raise ValidationError(f"`{self.callable}` is not a subclass of spadeapp.processes.executor.Executor")

        if self.history_provider_callable and "." not in self.history_provider_callable:
            raise ValidationError(f"`{self.history_provider_callable}` must be a fully qualified python path")

        if self.history_provider_callable:
            try:
                history_provider_callable = import_object(self.history_provider_callable)
            except (ImportError, AttributeError):
                raise ValidationError(f"`{self.history_provider_callable}` could not be imported")

            if not isinstance(history_provider_callable, type) or not issubclass(
                history_provider_callable, BaseHistoryProvider
            ):
                raise ValidationError(
                    f"`{self.history_provider_callable}` "
                    + "is not a subclass of spadeapp.processes.history_provider.HistoryProvider"
                )


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

    def __str__(self):
        return f"{self.process.code} - {self.created_at}"
