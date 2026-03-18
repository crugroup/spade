from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from spadeapp.files.models import File, FileFormat, FileProcessor
from spadeapp.processes.models import Executor, Process, ProcessRun

PREVIEW_FILES = (
    {
        "code": "Step 1: Volume Metadata",
        "description": "Ingestion for shared volume metadata",
        "tags": (
            "Bauxite & Alumina",
            "Stainless Steel",
            "Crude Steel",
            "Aluminium Carbon",
            "Manganese",
            "Aluminium Rolled",
            "Copper",
            "Copper Supply",
            "Primary Aluminium",
            "Phosphate",
            "Phosphate Rock",
            "Phosphate Fertilizer",
            "Urea",
            "Carbon Steel to Sigma",
        ),
    },
    {
        "code": "Step 2: Aluminium Carbon Products - Trade Ingestion",
        "description": "Ingestion for trade data for aluminium carbon products",
        "tags": ("Aluminium Carbon",),
    },
    {
        "code": "Step 2: Aluminium Carbon Products - Volume Ingestion",
        "description": "Ingestion for volume data for aluminium carbon products",
        "tags": ("Aluminium Carbon",),
    },
)


PREVIEW_PROCESSES = (
    {
        "code": "CPS - Freights to Datalab",
        "description": "Process freights data to Datalab",
        "tags": ("To Datalab", "CPS", "Freights"),
        "status": ProcessRun.Statuses.RUNNING,
        "result": None,
        "output": {"progress": "Previewing running state"},
        "error_message": None,
    },
    {
        "code": "Datahub - Business Glossary",
        "description": "",
        "tags": ("Datahub",),
        "status": ProcessRun.Statuses.ERROR,
        "result": ProcessRun.Results.FAILED,
        "output": {"stage": "validation"},
        "error_message": "Previewing failed state",
    },
    {
        "code": "Forecasted Prices Step 0: Metadata to Snowflake",
        "description": "",
        "tags": ("Forecasted Prices",),
        "status": ProcessRun.Statuses.FINISHED,
        "result": ProcessRun.Results.FAILED,
        "output": {"stage": "metadata export"},
        "error_message": "Previewing failed state",
    },
    {
        "code": "Forecasted Prices Step 2: Aluminium to Data Pipeline and Datalab",
        "description": "Export processed forecasted pricing data for Aluminium to Data Pipeline and Datalab",
        "tags": ("To Datalab", "To Datapipeline", "Forecasted Prices", "Aluminium Pricing"),
        "status": ProcessRun.Statuses.FINISHED,
        "result": ProcessRun.Results.SUCCESS,
        "output": {"rows": 142, "message": "Previewing success state"},
        "error_message": None,
    },
    {
        "code": "Forecasted Prices Step 2: Base Metals to Data Pipeline and Datalab",
        "description": "Export processed forecasted pricing data for Base Metals to Data Pipeline and Datalab",
        "tags": ("To Datalab", "To Datapipeline", "Forecasted Prices", "Base Metals Pricing"),
        "status": ProcessRun.Statuses.RUNNING,
        "result": None,
        "output": {"progress": "Previewing running state"},
        "error_message": None,
    },
)


class Command(BaseCommand):
    help = "Seed shared preview files and processes for local UI review"

    @staticmethod
    def _get_or_create_preview_file_processor() -> FileProcessor:
        processor_name = "Example File Processor"
        processor_callable = "spadeapp.examples.processor.ExampleFileProcessor"
        processor_description = "Example file processor for local preview data"

        file_processor = FileProcessor.objects.filter(callable=processor_callable).first()
        name_match = FileProcessor.objects.filter(name=processor_name).first()

        if file_processor is None and name_match is not None:
            file_processor = name_match
        elif file_processor is not None and name_match is not None and file_processor.pk != name_match.pk:
            raise CommandError(
                "Cannot seed preview layout because FileProcessor records already exist with the preview "
                "name and callable on different rows. Reconcile those duplicates first."
            )

        if file_processor is None:
            file_processor = FileProcessor.objects.create(
                name=processor_name,
                description=processor_description,
                callable=processor_callable,
            )
            return file_processor

        file_processor.name = processor_name
        file_processor.description = processor_description
        file_processor.callable = processor_callable
        file_processor.save()
        return file_processor

    @transaction.atomic
    def handle(self, *args, **options):
        user = get_user_model().objects.order_by("id").first()
        if user is None:
            raise CommandError("Create a user first so preview process runs can be attributed.")

        file_format = FileFormat.objects.filter(format="csv").first() or FileFormat.objects.order_by("id").first()
        if file_format is None:
            raise CommandError("No FileFormat found. Create one before seeding preview files.")

        file_processor = self._get_or_create_preview_file_processor()

        preview_executor, _ = Executor.objects.get_or_create(
            name="Local Preview Executor",
            defaults={
                "description": "Local executor for seeded preview process statuses",
                "callable": "spadeapp.examples.executor.ExampleExecutor",
                "history_provider_callable": None,
            },
        )
        preview_executor.description = "Local executor for seeded preview process statuses"
        preview_executor.callable = "spadeapp.examples.executor.ExampleExecutor"
        preview_executor.history_provider_callable = None
        preview_executor.save()

        seeded_files = []
        for preview_file in PREVIEW_FILES:
            file, _ = File.objects.get_or_create(
                code=preview_file["code"],
                defaults={
                    "description": preview_file["description"],
                    "format": file_format,
                    "processor": file_processor,
                    "system_params": {"seeded_from": "seed_preview_layout"},
                    "user_params": {"type": "object", "title": "Params", "properties": {}},
                },
            )
            file.description = preview_file["description"]
            file.format = file_format
            file.processor = file_processor
            file.system_params = {"seeded_from": "seed_preview_layout"}
            file.user_params = {"type": "object", "title": "Params", "properties": {}}
            file.save()
            file.tags.set(preview_file["tags"])
            seeded_files.append(file.code)

        seeded_processes = []
        for preview_process in PREVIEW_PROCESSES:
            process, _ = Process.objects.get_or_create(
                code=preview_process["code"],
                defaults={
                    "description": preview_process["description"],
                    "executor": preview_executor,
                    "system_params": {"seeded_from": "seed_preview_layout"},
                    "user_params": {"type": "object", "title": "Params", "properties": {}},
                },
            )
            process.description = preview_process["description"]
            process.executor = preview_executor
            process.system_params = {"seeded_from": "seed_preview_layout"}
            process.user_params = {"type": "object", "title": "Params", "properties": {}}
            process.save()
            process.tags.set(preview_process["tags"])

            ProcessRun.objects.filter(process=process).delete()
            ProcessRun.objects.create(
                process=process,
                user=user,
                status=preview_process["status"],
                result=preview_process["result"],
                system_params=process.system_params,
                user_params="{}",
                output=preview_process["output"],
                error_message=preview_process["error_message"],
            )
            seeded_processes.append(process.code)

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {len(seeded_files)} files and {len(seeded_processes)} processes for preview layout."
            )
        )
