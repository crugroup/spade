from django.db.models import QuerySet

from .models import FileVariableSets, ProcessVariableSets, Variable, VariableSet


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
        variables_dict = {}

        # Get all variable sets associated with the process
        process_variable_sets = (
            ProcessVariableSets.objects.filter(process_id=process_id)
            .select_related("variable_set")
            .prefetch_related("variable_set__variables")
        )

        for process_var_set in process_variable_sets:
            variable_set = process_var_set.variable_set
            variables_dict.update(variable_set.get_variables_dict())

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
        variables_dict = {}

        # Get all variable sets associated with the file
        file_variable_sets = (
            FileVariableSets.objects.filter(file_id=file_id)
            .select_related("variable_set")
            .prefetch_related("variable_set__variables")
        )

        for file_var_set in file_variable_sets:
            variable_set = file_var_set.variable_set
            variables_dict.update(variable_set.get_variables_dict())

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
        return VariableSet.objects.filter(processvariablesets__process_id=process_id).distinct()

    @staticmethod
    def get_variable_sets_for_file(file_id: int) -> QuerySet[VariableSet]:
        """
        Get all variable sets associated with a file.

        Args:
            file_id: The ID of the file

        Returns:
            QuerySet of VariableSet objects
        """
        return VariableSet.objects.filter(filevariablesets__file_id=file_id).distinct()

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
    def assign_variable_set_to_process(process_id: int, variable_set_id: int) -> ProcessVariableSets:
        """
        Assign a variable set to a process.

        Args:
            process_id: The ID of the process
            variable_set_id: The ID of the variable set

        Returns:
            Created ProcessVariableSets instance
        """
        return ProcessVariableSets.objects.create(process_id=process_id, variable_set_id=variable_set_id)

    @staticmethod
    def assign_variable_set_to_file(file_id: int, variable_set_id: int) -> FileVariableSets:
        """
        Assign a variable set to a file.

        Args:
            file_id: The ID of the file
            variable_set_id: The ID of the variable set

        Returns:
            Created FileVariableSets instance
        """
        return FileVariableSets.objects.create(file_id=file_id, variable_set_id=variable_set_id)

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
