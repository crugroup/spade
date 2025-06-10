from django.contrib.auth import get_user_model
from django.test import TestCase

from spadeapp.files.models import File, FileFormat, FileProcessor
from spadeapp.processes.models import Executor, Process

from .models import Variable, VariableSet
from .service import VariableService

User = get_user_model()


class VariableModelTest(TestCase):
    """Test cases for Variable model."""

    def test_create_regular_variable(self):
        """Test creating a regular (non-secret) variable."""
        variable = Variable.objects.create(
            name="TEST_VAR", value="test_value", description="Test variable", is_secret=False
        )
        self.assertEqual(variable.name, "TEST_VAR")
        self.assertEqual(variable.value, "test_value")
        self.assertEqual(variable.get_decrypted_value(), "test_value")
        self.assertFalse(variable.is_secret)

    def test_create_secret_variable(self):
        """Test creating a secret variable."""
        variable = Variable.objects.create(
            name="SECRET_VAR", value="secret_value", description="Secret variable", is_secret=True
        )
        self.assertEqual(variable.name, "SECRET_VAR")
        # Value should be encrypted
        self.assertNotEqual(variable.value, "secret_value")
        # But decrypted value should match original
        self.assertEqual(variable.get_decrypted_value(), "secret_value")
        self.assertTrue(variable.is_secret)

    def test_variable_str_representation(self):
        """Test string representation of Variable."""
        variable = Variable.objects.create(name="TEST_VAR", value="test")
        self.assertEqual(str(variable), "TEST_VAR")


class VariableSetModelTest(TestCase):
    """Test cases for VariableSet model."""

    def setUp(self):
        self.var1 = Variable.objects.create(name="VAR1", value="value1")
        self.var2 = Variable.objects.create(name="VAR2", value="value2", is_secret=True)

    def test_create_variable_set(self):
        """Test creating a variable set."""
        var_set = VariableSet.objects.create(name="test_set", description="Test variable set")
        var_set.variables.add(self.var1, self.var2)

        self.assertEqual(var_set.name, "test_set")
        self.assertEqual(var_set.variables.count(), 2)

    def test_get_variables_dict(self):
        """Test getting variables as dictionary."""
        var_set = VariableSet.objects.create(name="test_set")
        var_set.variables.add(self.var1, self.var2)

        variables_dict = var_set.get_variables_dict()
        self.assertEqual(variables_dict["VAR1"], "value1")
        self.assertEqual(variables_dict["VAR2"], "value2")  # Should be decrypted

    def test_variable_set_str_representation(self):
        """Test string representation of VariableSet."""
        var_set = VariableSet.objects.create(name="test_set")
        self.assertEqual(str(var_set), "test_set")


class VariableServiceTest(TestCase):
    """Test cases for VariableService."""

    def setUp(self):
        # Create test executor and process
        self.executor = Executor.objects.create(name="Test Executor", callable="test.executor.TestExecutor")
        self.process = Process.objects.create(code="test_process", executor=self.executor)

        # Create test file format, processor, and file
        self.file_format = FileFormat.objects.create(format="csv")
        self.file_processor = FileProcessor.objects.create(
            name="Test Processor", callable="test.processor.TestProcessor"
        )
        self.file = File.objects.create(code="test_file", format=self.file_format, processor=self.file_processor)

        # Create test variables and variable set
        self.var1 = Variable.objects.create(name="VAR1", value="value1")
        self.var2 = Variable.objects.create(name="VAR2", value="value2")
        self.var_set = VariableSet.objects.create(name="test_set")
        self.var_set.variables.add(self.var1, self.var2)

    def test_get_variables_for_process(self):
        """Test getting variables for a process."""
        # Assign variable set to process
        self.process.variable_sets.add(self.var_set)

        variables = VariableService.get_variables_for_process(self.process.id)
        self.assertEqual(variables["VAR1"], "value1")
        self.assertEqual(variables["VAR2"], "value2")

    def test_get_variables_for_file(self):
        """Test getting variables for a file."""
        # Assign variable set to file
        self.file.variable_sets.add(self.var_set)

        variables = VariableService.get_variables_for_file(self.file.id)
        self.assertEqual(variables["VAR1"], "value1")
        self.assertEqual(variables["VAR2"], "value2")

    def test_create_variable(self):
        """Test creating a variable through service."""
        variable = VariableService.create_variable(
            name="NEW_VAR", value="new_value", is_secret=True, description="New variable"
        )
        self.assertEqual(variable.name, "NEW_VAR")
        self.assertEqual(variable.get_decrypted_value(), "new_value")
        self.assertTrue(variable.is_secret)

    def test_merge_variables(self):
        """Test merging variable dictionaries."""
        dict1 = {"VAR1": "value1", "VAR2": "value2"}
        dict2 = {"VAR2": "new_value2", "VAR3": "value3"}

        merged = VariableService.merge_variables(dict1, dict2)
        self.assertEqual(merged["VAR1"], "value1")
        self.assertEqual(merged["VAR2"], "new_value2")  # Should be overridden
        self.assertEqual(merged["VAR3"], "value3")
