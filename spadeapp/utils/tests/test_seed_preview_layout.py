from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from spadeapp.files.models import FileFormat, FileProcessor
from spadeapp.processes.models import Process
from spadeapp.users.models import User


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
        self.assertEqual(Process.objects.count(), 5)
