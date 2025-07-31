from rest_framework import serializers

from .models import Variable, VariableSet


class VariableSerializer(serializers.ModelSerializer):
    """Serializer for Variable model."""

    class Meta:
        model = Variable
        fields = ["id", "name", "description", "value", "is_secret", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
        extra_kwargs = {"is_secret": {"required": False}}

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
        # Remove is_secret from validated_data to ensure it can't be changed
        if "is_secret" in validated_data:
            validated_data.pop("is_secret")

        # If it's a secret variable and no new value is provided, keep the old one
        if instance.is_secret and "value" in validated_data and not validated_data["value"]:
            validated_data.pop("value")

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class VariableSetSerializer(serializers.ModelSerializer):
    """Serializer for VariableSet model."""

    variables = serializers.PrimaryKeyRelatedField(queryset=Variable.objects.all(), many=True, required=False)

    class Meta:
        model = VariableSet
        fields = [
            "id",
            "name",
            "description",
            "variables",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class VariableSetDetailSerializer(VariableSetSerializer):
    """Detailed serializer for VariableSet with decrypted values (for internal use)."""

    variables_dict = serializers.SerializerMethodField()

    class Meta(VariableSetSerializer.Meta):
        fields = VariableSetSerializer.Meta.fields + ["variables_dict"]

    def get_variables_dict(self, obj):
        """Get variables as a dictionary with decrypted values."""
        return obj.get_variables_dict()
