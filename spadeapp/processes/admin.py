from django import forms
from django.contrib import admin

from . import models

# Register your models here.


class ProcessAdminForm(forms.ModelForm):
    class Meta:
        model = models.Process
        fields = "__all__"


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
        fields = "__all__"


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
        fields = "__all__"


class ExecutorAdmin(admin.ModelAdmin):
    form = ExecutorAdminForm
    list_display = ["name", "executor", "history_provider"]
    search_fields = ["name", "executor", "history_provider"]


admin.site.register(models.Executor, ExecutorAdmin)
