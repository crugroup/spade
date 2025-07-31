from django.db.models import QuerySet

from .models import Variable, VariableSet


class VariableService:
    """Service class for managing variables and variable sets."""

    @staticmethod
    def get_variables_for_process(process_id: int) -> dict[str, str]:
        """
        Get all variables for a specific process as a dictionary.

        Args:
            process_id: The ID of the process

        Returns:
            Dictionary of variable names and their decrypted values
        """
        from spadeapp.processes.models import Process

        variables_dict = {}

        try:
            process = Process.objects.prefetch_related("variable_sets__variables").get(id=process_id)

            # Get all variable sets associated with the process
            for variable_set in process.variable_sets.all():
                variables_dict.update(variable_set.get_variables_dict())
        except Process.DoesNotExist:
            pass

        return variables_dict

    @staticmethod
    def get_variables_for_file(file_id: int) -> dict[str, str]:
        """
        Get all variables for a specific file as a dictionary.

        Args:
            file_id: The ID of the file

        Returns:
            Dictionary of variable names and their decrypted values
        """
        from spadeapp.files.models import File

        variables_dict = {}

        try:
            file = File.objects.prefetch_related("variable_sets__variables").get(id=file_id)

            # Get all variable sets associated with the file
            for variable_set in file.variable_sets.all():
                variables_dict.update(variable_set.get_variables_dict())
        except File.DoesNotExist:
            pass

        return variables_dict

    @staticmethod
    def get_variables_for_variable_set(variable_set_id: int) -> dict[str, str]:
        """
        Get all variables for a specific variable set as a dictionary.

        Args:
            variable_set_id: The ID of the variable set

        Returns:
            Dictionary of variable names and their decrypted values
        """
        try:
            variable_set = VariableSet.objects.get(id=variable_set_id)
            return variable_set.get_variables_dict()
        except VariableSet.DoesNotExist:
            return {}

    @staticmethod
    def get_variable_sets_for_process(process_id: int) -> QuerySet[VariableSet]:
        """
        Get all variable sets associated with a process.

        Args:
            process_id: The ID of the process

        Returns:
            QuerySet of VariableSet objects
        """
        from spadeapp.processes.models import Process

        try:
            process = Process.objects.get(id=process_id)
            return process.variable_sets.all()
        except Process.DoesNotExist:
            return VariableSet.objects.none()

    @staticmethod
    def get_variable_sets_for_file(file_id: int) -> QuerySet[VariableSet]:
        """
        Get all variable sets associated with a file.

        Args:
            file_id: The ID of the file

        Returns:
            QuerySet of VariableSet objects
        """
        from spadeapp.files.models import File

        try:
            file = File.objects.get(id=file_id)
            return file.variable_sets.all()
        except File.DoesNotExist:
            return VariableSet.objects.none()

    @staticmethod
    def create_variable(name: str, value: str, is_secret: bool = False, description: str = "") -> Variable:
        """
        Create a new variable.

        Args:
            name: Variable name
            value: Variable value
            is_secret: Whether the variable is secret
            description: Variable description

        Returns:
            Created Variable instance
        """
        return Variable.objects.create(name=name, value=value, is_secret=is_secret, description=description)

    @staticmethod
    def create_variable_set(name: str, description: str = "", variable_ids: list[int] | None = None) -> VariableSet:
        """
        Create a new variable set.

        Args:
            name: Variable set name
            description: Variable set description
            variable_ids: List of variable IDs to add to the set

        Returns:
            Created VariableSet instance
        """
        variable_set = VariableSet.objects.create(name=name, description=description)

        if variable_ids:
            variables = Variable.objects.filter(id__in=variable_ids)
            variable_set.variables.set(variables)

        return variable_set

    @staticmethod
    def assign_variable_set_to_process(process_id: int, variable_set_id: int) -> bool:
        """
        Assign a variable set to a process.

        Args:
            process_id: The ID of the process
            variable_set_id: The ID of the variable set

        Returns:
            True if successful, False otherwise
        """
        from spadeapp.processes.models import Process

        try:
            process = Process.objects.get(id=process_id)
            variable_set = VariableSet.objects.get(id=variable_set_id)
            process.variable_sets.add(variable_set)
            return True
        except (Process.DoesNotExist, VariableSet.DoesNotExist):
            return False

    @staticmethod
    def assign_variable_set_to_file(file_id: int, variable_set_id: int) -> bool:
        """
        Assign a variable set to a file.

        Args:
            file_id: The ID of the file
            variable_set_id: The ID of the variable set

        Returns:
            True if successful, False otherwise
        """
        from spadeapp.files.models import File

        try:
            file = File.objects.get(id=file_id)
            variable_set = VariableSet.objects.get(id=variable_set_id)
            file.variable_sets.add(variable_set)
            return True
        except (File.DoesNotExist, VariableSet.DoesNotExist):
            return False

    @staticmethod
    def merge_variables(*variable_dicts: dict[str, str]) -> dict[str, str]:
        """
        Merge multiple variable dictionaries. Later dictionaries override earlier ones.

        Args:
            *variable_dicts: Variable dictionaries to merge

        Returns:
            Merged dictionary
        """
        merged = {}
        for var_dict in variable_dicts:
            merged.update(var_dict)
        return merged
