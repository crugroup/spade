# Generated by Django 5.0.3 on 2024-04-09 22:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("files", "0003_fileupload_rows_fileupload_size_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="fileformat",
            options={"ordering": ("-pk",)},
        ),
        migrations.AlterModelOptions(
            name="fileprocessor",
            options={"ordering": ("-pk",)},
        ),
    ]
