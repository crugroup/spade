from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from spadeapp.files.models import FileFormat, FileProcessor, FileUpload, ProcessFileLink
from spadeapp.processes.models import Process
from spadeapp.users.models import User
from spadeapp.utils.management.commands.seed_preview_layout import PREVIEW_FILES, PREVIEW_PROCESSES


class SeedPreviewLayoutCommandTest(TestCase):
    def setUp(self):
        User.objects.create_user(email="seed@example.com", password="pass12345")
        FileFormat.objects.create(format="csv")

    def test_reuses_existing_processor_with_same_callable(self):
        existing_processor = FileProcessor.objects.create(
            name="Legacy Preview Processor",
            description="old",
            callable="spadeapp.examples.processor.ExampleFileProcessor",
        )

        stdout = StringIO()
        call_command("seed_preview_layout", stdout=stdout)

        existing_processor.refresh_from_db()
        self.assertEqual(FileProcessor.objects.count(), 1)
        self.assertEqual(existing_processor.name, "Example File Processor")
        self.assertEqual(existing_processor.description, "Example file processor for local preview data")
        self.assertEqual(Process.objects.count(), len(PREVIEW_PROCESSES))

    def test_seeds_preview_uploads_and_one_move_links(self):
        call_command("seed_preview_layout", stdout=StringIO())

        expected_link_count = sum(len(preview_file["one_move_process_codes"]) for preview_file in PREVIEW_FILES)

        self.assertEqual(FileUpload.objects.count(), len(PREVIEW_FILES))
        self.assertEqual(ProcessFileLink.objects.count(), expected_link_count)
        self.assertTrue(Process.objects.filter(code="Step 3: Aluminium Rolled Products - Process to Sigma").exists())
        self.assertTrue(
            Process.objects.filter(code="Step 5: Publish to DataLab - Carbon Products Trade Classic").exists()
        )
