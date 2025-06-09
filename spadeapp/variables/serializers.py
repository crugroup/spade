from rest_framework import serializers

from .models import FileVariableSets, ProcessVariableSets, Variable, VariableSet


class VariableSerializer(serializers.ModelSerializer):
    """Serializer for Variable model."""

    class Meta:
        model = Variable
        fields = ["id", "name", "description", "value", "is_secret", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def to_representation(self, instance):
        """Hide secret variable values in API responses."""
        data = super().to_representation(instance)
        if instance.is_secret:
            data["value"] = "••••••••"  # Mask the value
        return data

    def create(self, validated_data):
        """Create a new variable."""
        return Variable.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """Update an existing variable."""
        # If it's a secret variable and no new value is provided, keep the old one
        if instance.is_secret and "value" in validated_data and not validated_data["value"]:
            validated_data.pop("value")

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class VariableSetSerializer(serializers.ModelSerializer):
    """Serializer for VariableSet model."""

    variables = VariableSerializer(many=True, read_only=True)
    variable_ids = serializers.PrimaryKeyRelatedField(
        queryset=Variable.objects.all(), many=True, write_only=True, source="variables"
    )
    variable_count = serializers.SerializerMethodField()

    class Meta:
        model = VariableSet
        fields = [
            "id",
            "name",
            "description",
            "variables",
            "variable_ids",
            "variable_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_variable_count(self, obj):
        """Get the number of variables in the set."""
        return obj.variables.count()


class ProcessVariableSetsSerializer(serializers.ModelSerializer):
    """Serializer for ProcessVariableSets model."""

    process_code = serializers.CharField(source="process.code", read_only=True)
    variable_set_name = serializers.CharField(source="variable_set.name", read_only=True)

    class Meta:
        model = ProcessVariableSets
        fields = ["id", "process", "process_code", "variable_set", "variable_set_name", "created_at"]
        read_only_fields = ["id", "created_at"]


class FileVariableSetsSerializer(serializers.ModelSerializer):
    """Serializer for FileVariableSets model."""

    file_code = serializers.CharField(source="file.code", read_only=True)
    variable_set_name = serializers.CharField(source="variable_set.name", read_only=True)

    class Meta:
        model = FileVariableSets
        fields = ["id", "file", "file_code", "variable_set", "variable_set_name", "created_at"]
        read_only_fields = ["id", "created_at"]


class VariableSetDetailSerializer(VariableSetSerializer):
    """Detailed serializer for VariableSet with decrypted values (for internal use)."""

    variables_dict = serializers.SerializerMethodField()

    class Meta(VariableSetSerializer.Meta):
        fields = VariableSetSerializer.Meta.fields + ["variables_dict"]

    def get_variables_dict(self, obj):
        """Get variables as a dictionary with decrypted values."""
        return obj.get_variables_dict()
