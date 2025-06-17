from django import forms
from django.contrib import admin

from . import models


class FileFormatAdminForm(forms.ModelForm):
    frictionless_schema = forms.JSONField(
        required=False,
        help_text="Frictionless data schema for validating files of this format",
        widget=forms.Textarea(attrs={"rows": 10, "cols": 80, "class": "vLargeTextField"}),
    )

    class Meta:
        model = models.FileFormat
        fields = ("format", "frictionless_schema")


class FileFormatAdmin(admin.ModelAdmin):
    form = FileFormatAdminForm
    list_display = ["format", "has_schema"]

    @admin.display(
        description="Has Schema",
        boolean=True,
    )
    def has_schema(self, obj):
        """Display whether the format has a frictionless schema."""
        return obj.frictionless_schema is not None


admin.site.register(models.FileFormat, FileFormatAdmin)


class FileProcessorAdminForm(forms.ModelForm):
    class Meta:
        model = models.FileProcessor
        fields = ("name", "description", "callable")


class FileProcessorAdmin(admin.ModelAdmin):
    form = FileProcessorAdminForm
    list_display = ["name", "description", "callable"]


admin.site.register(models.FileProcessor, FileProcessorAdmin)


class FileAdminForm(forms.ModelForm):
    class Meta:
        model = models.File
        fields = (
            "code",
            "description",
            "format",
            "processor",
            "tags",
            "user_params",
            "system_params",
            "linked_process",
        )


class FileAdmin(admin.ModelAdmin):
    form = FileAdminForm
    list_display = ["code", "description", "format", "processor", "created_at"]
    search_fields = ["code", "description"]
    list_filter = ["format", "processor", "created_at"]
    readonly_fields = ["created_at"]


admin.site.register(models.File, FileAdmin)


class FileUploadAdminForm(forms.ModelForm):
    class Meta:
        model = models.FileUpload
        fields = (
            "name",
            "output",
            "size",
            "rows",
            "user_params",
            "system_params",
        )


class FileUploadAdmin(admin.ModelAdmin):
    form = FileUploadAdminForm
    list_display = ["file", "result", "user", "created_at"]
    search_fields = ["file", "user"]
    list_filter = ["result", "created_at"]
    readonly_fields = ["file", "created_at"]


admin.site.register(models.FileUpload, FileUploadAdmin)
