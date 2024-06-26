# Generated by Django 5.0 on 2023-12-12 23:00

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("files", "0002_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="fileupload",
            name="rows",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="fileupload",
            name="size",
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="fileformat",
            name="format",
            field=models.CharField(max_length=30, unique=True),
        ),
        migrations.AlterField(
            model_name="fileprocessor",
            name="callable",
            field=models.CharField(max_length=512, unique=True),
        ),
        migrations.AlterField(
            model_name="fileprocessor",
            name="name",
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
