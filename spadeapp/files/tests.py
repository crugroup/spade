from django.core.exceptions import ValidationError
from django.test import TestCase

from .models import FileFormat


class FileFormatModelTest(TestCase):
    """Test cases for FileFormat model."""

    def test_create_file_format_without_schema(self):
        """Test creating a FileFormat without frictionless_schema."""
        file_format = FileFormat.objects.create(format="csv")
        self.assertEqual(file_format.format, "csv")
        self.assertIsNone(file_format.frictionless_schema)

    def test_create_file_format_with_valid_schema(self):
        """Test creating a FileFormat with a valid frictionless schema."""
        valid_schema = {"fields": [{"name": "name", "type": "string"}, {"name": "age", "type": "integer"}]}
        file_format = FileFormat.objects.create(format="csv", frictionless_schema=valid_schema)
        self.assertEqual(file_format.format, "csv")
        self.assertEqual(file_format.frictionless_schema, valid_schema)

    def test_validate_valid_frictionless_schema(self):
        """Test validation passes with valid frictionless schema."""
        valid_schema = {"fields": [{"name": "name", "type": "string"}, {"name": "age", "type": "integer"}]}
        file_format = FileFormat(format="csv", frictionless_schema=valid_schema)

        # This should not raise an error
        try:
            file_format.full_clean()
        except ValidationError:
            self.fail("full_clean() raised ValidationError unexpectedly!")

    def test_validate_valid_schema_with_constraints(self):
        """Test validation passes with frictionless schema including constraints."""
        valid_schema = {
            "fields": [
                {
                    "name": "email",
                    "type": "string",
                    "constraints": {"pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"},
                },
                {"name": "score", "type": "number", "constraints": {"minimum": 0, "maximum": 100}},
            ]
        }
        file_format = FileFormat(format="json", frictionless_schema=valid_schema)

        # This should not raise an error
        try:
            file_format.full_clean()
        except ValidationError:
            self.fail("full_clean() raised ValidationError unexpectedly!")

    def test_validate_invalid_schema_empty_dict(self):
        """Test validation passes when schema is an empty dictionary (valid minimal schema)."""
        file_format = FileFormat(format="yaml", frictionless_schema={})

        # Empty dict is a valid minimal frictionless schema
        try:
            file_format.full_clean()
        except ValidationError:
            self.fail("full_clean() raised ValidationError unexpectedly for empty dict!")

    def test_validate_invalid_frictionless_schema(self):
        """Test validation fails with an invalid frictionless schema structure."""
        # This is an invalid schema because it has an invalid field type
        invalid_schema = {"fields": [{"name": "name", "type": "invalid_type_that_does_not_exist"}]}
        file_format = FileFormat(format="json", frictionless_schema=invalid_schema)

        with self.assertRaises(ValidationError):
            file_format.full_clean()

    def test_validate_complex_valid_schema(self):
        """Test validation passes with a complex valid frictionless schema."""
        complex_schema = {
            "fields": [
                {"name": "id", "type": "integer", "constraints": {"minimum": 1}},
                {"name": "name", "type": "string", "constraints": {"minLength": 1, "maxLength": 100}},
                {"name": "score", "type": "number", "constraints": {"minimum": 0.0, "maximum": 100.0}},
            ],
            "primaryKey": ["id"],
        }
        file_format = FileFormat(format="parquet", frictionless_schema=complex_schema)

        # This should not raise an error
        try:
            file_format.full_clean()
        except ValidationError:
            self.fail("full_clean() raised ValidationError unexpectedly!")

    def test_static_validate_method(self):
        """Test the static validate_frictionless_schema method directly."""
        valid_schema = {"fields": [{"name": "name", "type": "string"}, {"name": "age", "type": "integer"}]}

        # This should not raise an error
        try:
            FileFormat.validate_frictionless_schema(valid_schema)
        except ValidationError:
            self.fail("validate_frictionless_schema() raised ValidationError unexpectedly!")

    def test_comprehensive_frictionless_schema_example(self):
        """Test a comprehensive real-world frictionless schema example."""
        # This is a realistic frictionless schema for a customer data file
        customer_schema = {
            "fields": [
                {"name": "customer_id", "type": "integer", "constraints": {"minimum": 1, "required": True}},
                {"name": "email", "type": "string", "format": "email", "constraints": {"required": True}},
                {
                    "name": "first_name",
                    "type": "string",
                    "constraints": {"minLength": 1, "maxLength": 50, "required": True},
                },
                {
                    "name": "last_name",
                    "type": "string",
                    "constraints": {"minLength": 1, "maxLength": 50, "required": True},
                },
                {"name": "age", "type": "integer", "constraints": {"minimum": 0, "maximum": 150}},
                {"name": "registration_date", "type": "date"},
                {"name": "is_active", "type": "boolean"},
                {"name": "account_balance", "type": "number", "constraints": {"minimum": 0.0}},
            ],
            "primaryKey": ["customer_id"],
            "title": "Customer Data Schema",
            "description": "Schema for validating customer data files",
        }

        file_format = FileFormat.objects.create(format="customer_csv", frictionless_schema=customer_schema)

        self.assertEqual(file_format.format, "customer_csv")
        self.assertEqual(file_format.frictionless_schema, customer_schema)

        # Verify the schema can be validated without errors
        try:
            file_format.full_clean()
        except ValidationError:
            self.fail("full_clean() raised ValidationError unexpectedly for comprehensive schema!")

    def test_validate_invalid_data_type(self):
        """Test validation fails when schema data is not a dictionary."""
        with self.assertRaises(ValidationError):
            FileFormat.validate_frictionless_schema("not a dict")
