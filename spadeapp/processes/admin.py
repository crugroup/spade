from django import forms
from django.contrib import admin

from . import models

# Register your models here.


class ProcessAdminForm(forms.ModelForm):
    class Meta:
        model = models.Process
        fields = ("code", "description", "tags", "system_params", "user_params", "executor")


class ProcessAdmin(admin.ModelAdmin):
    form = ProcessAdminForm
    list_display = ["code", "description", "executor", "created_at"]
    search_fields = ["code", "description"]
    list_filter = ["executor", "created_at"]
    readonly_fields = ["created_at"]


admin.site.register(models.Process, ProcessAdmin)


class ProcessRunAdminForm(forms.ModelForm):
    class Meta:
        model = models.ProcessRun
        fields = (
            "process",
            "result",
            "status",
            "user",
            "system_params",
            "user_params",
            "output",
            "error_message",
        )


class ProcessRunAdmin(admin.ModelAdmin):
    form = ProcessRunAdminForm
    list_display = ["process", "result", "status", "user", "created_at"]
    search_fields = ["process", "user"]
    list_filter = ["result", "status", "created_at"]
    readonly_fields = ["created_at"]


admin.site.register(models.ProcessRun, ProcessRunAdmin)


class ExecutorAdminForm(forms.ModelForm):
    class Meta:
        model = models.Executor
        fields = ("name", "description", "callable", "history_provider_callable")


class ExecutorAdmin(admin.ModelAdmin):
    form = ExecutorAdminForm
    list_display = ["name", "description", "callable", "history_provider_callable"]
    search_fields = ["name", "description", "callable", "history_provider_callable"]


admin.site.register(models.Executor, ExecutorAdmin)
