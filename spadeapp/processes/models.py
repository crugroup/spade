from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from rules.contrib.models import RulesModel
from spadesdk.executor import Executor as SDKExecutor
from spadesdk.history_provider import HistoryProvider as SDKHistoryProvider
from taggit.managers import TaggableManager

from ..utils.imports import import_object
from ..utils.rules import defer_rule


class Executor(RulesModel):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    callable = models.CharField(max_length=512)
    history_provider_callable = models.CharField(max_length=512, null=True, blank=True)

    class Meta:
        ordering = ("-pk",)
        rules_permissions = {
            "add": defer_rule("processes.add_executor"),
            "view": defer_rule("processes.view_executor"),
            "list": defer_rule("processes.list_executor"),
            "change": defer_rule("processes.change_executor"),
            "delete": defer_rule("processes.delete_executor"),
        }

    def __str__(self):
        return self.name

    def clean(self):
        self.validate(self.callable, self.history_provider_callable)

    @staticmethod
    def validate(
        callable_value: str,
        history_provider_callable_value: str | None,
        exception_class=ValidationError,
    ):
        if "." not in callable_value:
            raise ValidationError(f"`{callable_value}` must be a fully qualified python path")

        try:
            executor_callable = import_object(callable_value)
        except (ImportError, AttributeError):
            raise ValidationError(f"`{callable_value}` could not be imported")

        if not isinstance(executor_callable, type) or not issubclass(executor_callable, SDKExecutor):
            raise ValidationError(f"`{callable_value}` is not a subclass of spadesdk.executor.Executor")

        if history_provider_callable_value and "." not in history_provider_callable_value:
            raise ValidationError(f"`{history_provider_callable_value}` must be a fully qualified python path")

        if history_provider_callable_value:
            try:
                history_provider_callable = import_object(history_provider_callable_value)
            except (ImportError, AttributeError):
                raise ValidationError(f"`{history_provider_callable_value}` could not be imported")

            if not isinstance(history_provider_callable, type) or not issubclass(
                history_provider_callable, SDKHistoryProvider
            ):
                raise ValidationError(
                    f"`{history_provider_callable_value}` "
                    + "is not a subclass of spadesdk.history_provider.HistoryProvider"
                )


class Process(RulesModel):
    code = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
    tags = TaggableManager(blank=True)
    executor = models.ForeignKey(Executor, on_delete=models.CASCADE)
    system_params = models.JSONField(null=True, blank=True)
    user_params = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-pk",)
        rules_permissions = {
            "add": defer_rule("processes.add_process"),
            "view": defer_rule("processes.view_process"),
            "list": defer_rule("processes.list_process"),
            "change": defer_rule("processes.change_process"),
            "delete": defer_rule("processes.delete_process"),
        }

    def __str__(self):
        return self.code


class ProcessRun(RulesModel):
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
    status = models.CharField(max_length=20, choices=Statuses, default=Statuses.NEW)
    result = models.CharField(max_length=20, choices=Results, null=True, blank=True)
    system_params = models.JSONField(null=True, blank=True)
    user_params = models.JSONField(null=True, blank=True)
    output = models.JSONField(null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.PROTECT)
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-pk",)
        rules_permissions = {
            "add": defer_rule("processes.add_processrun"),
            "view": defer_rule("processes.view_processrun"),
            "list": defer_rule("processes.list_processrun"),
            "change": defer_rule("processes.change_processrun"),
            "delete": defer_rule("processes.delete_processrun"),
        }

    def __str__(self):
        return f"{self.process.code} - {self.created_at}"
