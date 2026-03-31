from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("processes", "0001_initial"),
        ("files", "0006_fileformat_frictionless_schema"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProcessFileLink",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "file",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="one_move_links",
                        to="files.file",
                    ),
                ),
                (
                    "process",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="one_move_links",
                        to="processes.process",
                    ),
                ),
            ],
            options={
                "ordering": ("-pk",),
            },
        ),
        migrations.AddConstraint(
            model_name="processfilelink",
            constraint=models.UniqueConstraint(
                fields=("file", "process"),
                name="files_processfilelink_unique_file_process",
            ),
        ),
    ]