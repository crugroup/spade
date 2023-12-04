from django import forms
from django.contrib import admin

from . import models


class FileFormatAdminForm(forms.ModelForm):
    class Meta:
        model = models.FileFormat
        fields = "__all__"


class FileFormatAdmin(admin.ModelAdmin):
    form = FileFormatAdminForm
    list_display = ["format"]


admin.site.register(models.FileFormat, FileFormatAdmin)


class FileProcessorAdminForm(forms.ModelForm):
    class Meta:
        model = models.FileProcessor
        fields = "__all__"


class FileProcessorAdmin(admin.ModelAdmin):
    form = FileProcessorAdminForm
    list_display = ["processor"]


admin.site.register(models.FileProcessor, FileProcessorAdmin)


class FileAdminForm(forms.ModelForm):
    class Meta:
        model = models.File
        fields = "__all__"


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
        fields = "__all__"


class FileUploadAdmin(admin.ModelAdmin):
    form = FileUploadAdminForm
    list_display = ["file", "result", "user", "created_at"]
    search_fields = ["file", "user"]
    list_filter = ["result", "created_at"]
    readonly_fields = ["created_at"]


admin.site.register(models.FileUpload, FileUploadAdmin)
