# Generated by Django 5.0 on 2023-12-05 09:24

import django.db.models.deletion
import taggit.managers
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("files", "0001_initial"),
        ("processes", "0001_initial"),
        ("taggit", "0006_rename_taggeditem_content_type_object_id_taggit_tagg_content_8fc721_idx"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="file",
            name="linked_process",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="processes.process"
            ),
        ),
        migrations.AddField(
            model_name="file",
            name="tags",
            field=taggit.managers.TaggableManager(
                blank=True,
                help_text="A comma-separated list of tags.",
                through="taggit.TaggedItem",
                to="taggit.Tag",
                verbose_name="Tags",
            ),
        ),
        migrations.AddField(
            model_name="file",
            name="format",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="files.fileformat"),
        ),
        migrations.AddField(
            model_name="file",
            name="processor",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="files.fileprocessor"),
        ),
        migrations.AddField(
            model_name="fileupload",
            name="file",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="files.file"),
        ),
        migrations.AddField(
            model_name="fileupload",
            name="linked_process_run",
            field=models.OneToOneField(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="processes.processrun"
            ),
        ),
        migrations.AddField(
            model_name="fileupload",
            name="user",
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
    ]
