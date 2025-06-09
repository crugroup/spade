import base64

from cryptography.fernet import Fernet
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from rules.contrib.models import RulesModel

from ..utils.permissions import defer_rule


class Variable(RulesModel):
    """Model representing a variable with name and value."""

    name = models.CharField(max_length=100, unique=True, help_text="Variable name")
    description = models.TextField(null=True, blank=True, help_text="Variable description")
    value = models.TextField(help_text="Variable value")
    is_secret = models.BooleanField(default=False, help_text="Whether this variable is secret")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name",)
        rules_permissions = {
            "add": defer_rule("variables.add_variable"),
            "view": defer_rule("variables.view_variable"),
            "list": defer_rule("variables.list_variable"),
            "change": defer_rule("variables.change_variable"),
            "delete": defer_rule("variables.delete_variable"),
        }

    def __str__(self):
        return self.name

    def _get_encryption_key(self):
        """Get or create encryption key for secret variables."""
        secret_key = getattr(settings, "SECRET_KEY", None)
        if not secret_key:
            raise ValueError("SECRET_KEY not found in settings")

        # Create a consistent key from SECRET_KEY
        key = base64.urlsafe_b64encode(secret_key.encode()[:32].ljust(32, b"0"))
        return key

    def save(self, *args, **kwargs):
        """Override save to encrypt secret variables."""
        if self.is_secret and self.value:
            # Encrypt the value if it's a secret and not already encrypted
            if not self.value.startswith("gAAAAAB"):  # Fernet tokens start with this
                fernet = Fernet(self._get_encryption_key())
                self.value = fernet.encrypt(self.value.encode()).decode()
        super().save(*args, **kwargs)

    def get_decrypted_value(self):
        """Get the decrypted value for secret variables."""
        if not self.is_secret:
            return self.value

        try:
            fernet = Fernet(self._get_encryption_key())
            return fernet.decrypt(self.value.encode()).decode()
        except Exception:
            # If decryption fails, return the original value
            return self.value

    def clean(self):
        """Validate the variable."""
        super().clean()
        if not self.name:
            raise ValidationError("Variable name is required")
        if not self.name.replace("_", "").replace("-", "").isalnum():
            raise ValidationError("Variable name can only contain letters, numbers, underscores, and hyphens")


class VariableSet(RulesModel):
    """Model representing a set of variables."""

    name = models.CharField(max_length=100, unique=True, help_text="Variable set name")
    description = models.TextField(null=True, blank=True, help_text="Variable set description")
    variables = models.ManyToManyField(Variable, blank=True, help_text="Variables in this set")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name",)
        rules_permissions = {
            "add": defer_rule("variables.add_variableset"),
            "view": defer_rule("variables.view_variableset"),
            "list": defer_rule("variables.list_variableset"),
            "change": defer_rule("variables.change_variableset"),
            "delete": defer_rule("variables.delete_variableset"),
        }

    def __str__(self):
        return self.name

    def get_variables_dict(self):
        """Get all variables in this set as a dictionary with decrypted values."""
        variables_dict = {}
        for variable in self.variables.all():
            variables_dict[variable.name] = variable.get_decrypted_value()
        return variables_dict


class ProcessVariableSets(RulesModel):
    """Model representing the relationship between a process and variable sets."""

    process = models.ForeignKey(
        "processes.Process", on_delete=models.CASCADE, help_text="Process that uses these variable sets"
    )
    variable_set = models.ForeignKey(
        VariableSet, on_delete=models.CASCADE, help_text="Variable set to be used by the process"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("process", "variable_set")
        ordering = ("process__code", "variable_set__name")
        verbose_name = "Process Variable Set"
        verbose_name_plural = "Process Variable Sets"
        rules_permissions = {
            "add": defer_rule("variables.add_processvariablesets"),
            "view": defer_rule("variables.view_processvariablesets"),
            "list": defer_rule("variables.list_processvariablesets"),
            "change": defer_rule("variables.change_processvariablesets"),
            "delete": defer_rule("variables.delete_processvariablesets"),
        }

    def __str__(self):
        return f"{self.process.code} - {self.variable_set.name}"


class FileVariableSets(RulesModel):
    """Model representing the relationship between a file and variable sets."""

    file = models.ForeignKey("files.File", on_delete=models.CASCADE, help_text="File that uses these variable sets")
    variable_set = models.ForeignKey(
        VariableSet, on_delete=models.CASCADE, help_text="Variable set to be used by the file"
    )
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("file", "variable_set")
        ordering = ("file__code", "variable_set__name")
        verbose_name = "File Variable Set"
        verbose_name_plural = "File Variable Sets"
        rules_permissions = {
            "add": defer_rule("variables.add_filevariablesets"),
            "view": defer_rule("variables.view_filevariablesets"),
            "list": defer_rule("variables.list_filevariablesets"),
            "change": defer_rule("variables.change_filevariablesets"),
            "delete": defer_rule("variables.delete_filevariablesets"),
        }

    def __str__(self):
        return f"{self.file.code} - {self.variable_set.name}"
