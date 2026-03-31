from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from spadeapp.files.models import File, FileFormat, FileProcessor, FileUpload, ProcessFileLink
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
        "linked_process_code": None,
        "one_move_process_codes": (),
    },
    {
        "code": "Step 2: Aluminium Carbon Products - Trade Ingestion",
        "description": "Ingestion for trade data for aluminium carbon products",
        "tags": ("Aluminium Carbon", "Carbon Products"),
        "linked_process_code": "Step 3: Aluminium Carbon Products - Process to Sigma",
        "one_move_process_codes": ("Step 5: Publish to DataLab - Carbon Products Trade Classic",),
    },
    {
        "code": "Step 2: Aluminium Carbon Products - Volume Ingestion",
        "description": "Ingestion for volume data for aluminium carbon products",
        "tags": ("Aluminium Carbon", "Carbon Products"),
        "linked_process_code": "Step 3: Aluminium Carbon Products - Process to Sigma",
        "one_move_process_codes": (),
    },
    {
        "code": "Step 2: Aluminium Rolled Products - Volume Ingestion",
        "description": "Ingestion for volume data for aluminium rolled products",
        "tags": ("Aluminium Rolled",),
        "linked_process_code": "Step 3: Aluminium Rolled Products - Process to Sigma",
        "one_move_process_codes": (
            "Step 4: Aluminium Rolled Products Market Outlook - Process to Datapipeline",
            "Step 4: Aluminium Rolled Products Monitors - Process to Datapipeline",
        ),
    },
    {
        "code": "Step 2: Phosphate Fertilizer - Volume Ingestion",
        "description": "Ingestion for phosphate fertilizer volume data",
        "tags": ("Phosphate Fertilizer", "Phosphate"),
        "linked_process_code": "Step 3: Phosphate Fertilizer - Process to Sigma",
        "one_move_process_codes": ("Step 4: Phosphate Fertilizer - Process to Datapipeline",),
    },
    {
        "code": "Step 2: Copper Supply - Volume Ingestion",
        "description": "Ingestion for copper supply volume data",
        "tags": ("Copper Supply", "Copper"),
        "linked_process_code": "Step 3: Copper Supply - Process to Sigma",
        "one_move_process_codes": ("Step 4: Copper Supply - Process to Datapipeline",),
    },
    {
        "code": "Step 2: Finished Steel Products - Market Outlook Ingestion",
        "description": "Ingestion for steel finished products market outlook data",
        "tags": ("Forecasted Prices", "Finished Steel"),
        "linked_process_code": "Step 3: Finished Steel Market Outlook - Process To Sigma",
        "one_move_process_codes": (),
    },
    {
        "code": "Step 2: Finished Steel Products - Monitors Ingestion",
        "description": "Ingestion for steel finished products monitors data",
        "tags": ("Forecasted Prices", "Finished Steel"),
        "linked_process_code": "Step 3: Finished Steel Monitors - Process To Sigma",
        "one_move_process_codes": ("Step 4: Finished Steel Monitors - Process To Datapipeline",),
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
    {
        "code": "Step 3: Aluminium Carbon Products - Process to Sigma",
        "description": "Send prepared carbon products data to Sigma for analyst review",
        "tags": ("Aluminium Carbon", "Carbon Products", "To Sigma"),
        "status": ProcessRun.Statuses.FINISHED,
        "result": ProcessRun.Results.SUCCESS,
        "output": {"stage": "sigma", "message": "Previewing Sigma handoff success"},
        "error_message": None,
    },
    {
        "code": "Step 5: Publish to DataLab - Carbon Products Trade Classic",
        "description": "After Sigma review, publish carbon products trade data to DataLab",
        "tags": ("Carbon Products", "To Datalab"),
        "status": ProcessRun.Statuses.RUNNING,
        "result": None,
        "output": {"progress": "Previewing DataLab publish in progress"},
        "error_message": None,
    },
    {
        "code": "Step 3: Aluminium Rolled Products - Process to Sigma",
        "description": "Send prepared aluminium rolled data to Sigma for analyst review",
        "tags": ("Aluminium Rolled", "To Sigma"),
        "status": ProcessRun.Statuses.FINISHED,
        "result": ProcessRun.Results.SUCCESS,
        "output": {"stage": "sigma", "message": "Previewing Sigma handoff success"},
        "error_message": None,
    },
    {
        "code": "Step 4: Aluminium Rolled Products Market Outlook - Process to Datapipeline",
        "description": "After Sigma review, publish aluminium rolled market outlook data to Datapipeline",
        "tags": ("Aluminium Rolled", "To Datapipeline"),
        "status": ProcessRun.Statuses.FINISHED,
        "result": ProcessRun.Results.SUCCESS,
        "output": {"rows": 188, "message": "Previewing post-Sigma datapipeline success"},
        "error_message": None,
    },
    {
        "code": "Step 4: Aluminium Rolled Products Monitors - Process to Datapipeline",
        "description": "After Sigma review, publish aluminium rolled monitors data to Datapipeline",
        "tags": ("Aluminium Rolled", "To Datapipeline"),
        "status": ProcessRun.Statuses.RUNNING,
        "result": None,
        "output": {"progress": "Previewing post-Sigma datapipeline run"},
        "error_message": None,
    },
    {
        "code": "Step 3: Phosphate Fertilizer - Process to Sigma",
        "description": "Send prepared phosphate fertilizer data to Sigma for analyst review",
        "tags": ("Phosphate Fertilizer", "Phosphate", "To Sigma"),
        "status": ProcessRun.Statuses.FINISHED,
        "result": ProcessRun.Results.SUCCESS,
        "output": {"stage": "sigma", "message": "Previewing Sigma handoff success"},
        "error_message": None,
    },
    {
        "code": "Step 4: Phosphate Fertilizer - Process to Datapipeline",
        "description": "After Sigma review, publish phosphate fertilizer data to Datapipeline",
        "tags": ("Phosphate Fertilizer", "Phosphate", "To Datapipeline"),
        "status": ProcessRun.Statuses.ERROR,
        "result": ProcessRun.Results.FAILED,
        "output": {"stage": "delivery", "message": "Previewing failed post-Sigma delivery"},
        "error_message": "Previewing failed datapipeline publish",
    },
    {
        "code": "Step 3: Copper Supply - Process to Sigma",
        "description": "Send prepared copper supply data to Sigma for analyst review",
        "tags": ("Copper Supply", "Copper", "To Sigma"),
        "status": ProcessRun.Statuses.RUNNING,
        "result": None,
        "output": {"progress": "Previewing Sigma handoff in progress"},
        "error_message": None,
    },
    {
        "code": "Step 4: Copper Supply - Process to Datapipeline",
        "description": "After Sigma review, publish copper supply data to Datapipeline",
        "tags": ("Copper Supply", "Copper", "To Datapipeline"),
        "status": ProcessRun.Statuses.FINISHED,
        "result": ProcessRun.Results.SUCCESS,
        "output": {"rows": 96, "message": "Previewing post-Sigma datapipeline success"},
        "error_message": None,
    },
    {
        "code": "Step 3: Finished Steel Market Outlook - Process To Sigma",
        "description": "Send finished steel market outlook data to Sigma for analyst review",
        "tags": ("Forecasted Prices", "Finished Steel", "To Sigma"),
        "status": ProcessRun.Statuses.FINISHED,
        "result": ProcessRun.Results.SUCCESS,
        "output": {"stage": "sigma", "message": "Previewing Sigma handoff success"},
        "error_message": None,
    },
    {
        "code": "Step 3: Finished Steel Monitors - Process To Sigma",
        "description": "Send finished steel monitors data to Sigma for analyst review",
        "tags": ("Forecasted Prices", "Finished Steel", "To Sigma"),
        "status": ProcessRun.Statuses.RUNNING,
        "result": None,
        "output": {"progress": "Previewing Sigma handoff in progress"},
        "error_message": None,
    },
    {
        "code": "Step 4: Finished Steel Monitors - Process To Datapipeline",
        "description": "After Sigma review, publish finished steel monitors data to Datapipeline",
        "tags": ("Forecasted Prices", "Finished Steel", "To Datapipeline"),
        "status": ProcessRun.Statuses.FINISHED,
        "result": ProcessRun.Results.SUCCESS,
        "output": {"rows": 123, "message": "Previewing post-Sigma datapipeline success"},
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

        processes_by_code: dict[str, Process] = {}
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
            processes_by_code[process.code] = process

        seeded_files = []
        upload_count = 0
        link_count = 0
        for index, preview_file in enumerate(PREVIEW_FILES):
            linked_process = processes_by_code.get(preview_file["linked_process_code"])
            file, _ = File.objects.get_or_create(
                code=preview_file["code"],
                defaults={
                    "description": preview_file["description"],
                    "format": file_format,
                    "processor": file_processor,
                    "linked_process": linked_process,
                    "system_params": {"seeded_from": "seed_preview_layout"},
                    "user_params": {"type": "object", "title": "Params", "properties": {}},
                },
            )
            file.description = preview_file["description"]
            file.format = file_format
            file.processor = file_processor
            file.linked_process = linked_process
            file.system_params = {"seeded_from": "seed_preview_layout"}
            file.user_params = {"type": "object", "title": "Params", "properties": {}}
            file.save()
            file.tags.set(preview_file["tags"])
            seeded_files.append(file.code)

            for linked_process_code in preview_file["one_move_process_codes"]:
                workflow_process = processes_by_code.get(linked_process_code)
                if workflow_process is None:
                    continue
                _, created = ProcessFileLink.objects.get_or_create(file=file, process=workflow_process)
                if created:
                    link_count += 1

            FileUpload.objects.filter(file=file, system_params__seeded_from="seed_preview_layout").delete()
            FileUpload.objects.create(
                file=file,
                name=self._build_preview_upload_name(file.code),
                result=self._build_preview_upload_result(index),
                system_params={"seeded_from": "seed_preview_layout"},
                user_params="{}",
                output={"seeded_from": "seed_preview_layout", "file_code": file.code},
                size=12_000 + (index * 512),
                rows=140 + (index * 7),
                error_message=(
                    "Previewing upload validation issue"
                    if self._build_preview_upload_result(index) == FileUpload.Results.FAILED
                    else None
                ),
                user=user,
            )
            upload_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                "Seeded "
                + f"{len(seeded_files)} files, "
                + f"{len(seeded_processes)} processes, "
                + f"{link_count} OneMove links, and "
                + f"{upload_count} preview uploads for preview layout."
            )
        )

    @staticmethod
    def _build_preview_upload_name(file_code: str) -> str:
        normalized_code = file_code.lower().replace(" ", "-").replace(":", "").replace("/", "-")
        return f"preview-{normalized_code}.csv"

    @staticmethod
    def _build_preview_upload_result(index: int):
        results = [
            FileUpload.Results.SUCCESS,
            FileUpload.Results.WARNING,
            FileUpload.Results.FAILED,
        ]
        return results[index % len(results)]
