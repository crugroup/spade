from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from .models import FileVariableSets, ProcessVariableSets, Variable, VariableSet
from .serializers import (
    FileVariableSetsSerializer,
    ProcessVariableSetsSerializer,
    VariableSerializer,
    VariableSetSerializer,
)


@extend_schema_view(
    list=extend_schema(description="List all variables"),
    create=extend_schema(description="Create a new variable"),
    retrieve=extend_schema(description="Retrieve a variable"),
    update=extend_schema(description="Update a variable"),
    partial_update=extend_schema(description="Partially update a variable"),
    destroy=extend_schema(description="Delete a variable"),
)
class VariableViewSet(viewsets.ModelViewSet):
    """ViewSet for managing variables."""

    queryset = Variable.objects.all()
    serializer_class = VariableSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["is_secret"]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at", "updated_at"]
    ordering = ["name"]

    @extend_schema(
        description="Get the decrypted value of a variable (for authorized users only)",
        responses={200: {"type": "object", "properties": {"value": {"type": "string"}}}},
    )
    @action(detail=True, methods=["get"])
    def value(self, request, pk=None):
        """Get the decrypted value of a variable."""
        variable = self.get_object()
        return Response({"value": variable.get_decrypted_value()})


@extend_schema_view(
    list=extend_schema(description="List all variable sets"),
    create=extend_schema(description="Create a new variable set"),
    retrieve=extend_schema(description="Retrieve a variable set"),
    update=extend_schema(description="Update a variable set"),
    partial_update=extend_schema(description="Partially update a variable set"),
    destroy=extend_schema(description="Delete a variable set"),
)
class VariableSetViewSet(viewsets.ModelViewSet):
    """ViewSet for managing variable sets."""

    queryset = VariableSet.objects.prefetch_related("variables").all()
    serializer_class = VariableSetSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at", "updated_at"]
    ordering = ["name"]

    @extend_schema(
        description="Get all variables in the set as a dictionary with decrypted values",
        responses={200: {"type": "object", "additionalProperties": {"type": "string"}}},
    )
    @action(detail=True, methods=["get"])
    def variables_dict(self, request, pk=None):
        """Get all variables in the set as a dictionary."""
        variable_set = self.get_object()
        return Response(variable_set.get_variables_dict())

    @extend_schema(
        description="Add variables to the set",
        request={"type": "object", "properties": {"variable_ids": {"type": "array", "items": {"type": "integer"}}}},
        responses={200: VariableSetSerializer},
    )
    @action(detail=True, methods=["post"])
    def add_variables(self, request, pk=None):
        """Add variables to the set."""
        variable_set = self.get_object()
        variable_ids = request.data.get("variable_ids", [])

        variables = Variable.objects.filter(id__in=variable_ids)
        variable_set.variables.add(*variables)

        serializer = self.get_serializer(variable_set)
        return Response(serializer.data)

    @extend_schema(
        description="Remove variables from the set",
        request={"type": "object", "properties": {"variable_ids": {"type": "array", "items": {"type": "integer"}}}},
        responses={200: VariableSetSerializer},
    )
    @action(detail=True, methods=["post"])
    def remove_variables(self, request, pk=None):
        """Remove variables from the set."""
        variable_set = self.get_object()
        variable_ids = request.data.get("variable_ids", [])

        variables = Variable.objects.filter(id__in=variable_ids)
        variable_set.variables.remove(*variables)

        serializer = self.get_serializer(variable_set)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(description="List all process variable set relationships"),
    create=extend_schema(description="Create a new process variable set relationship"),
    retrieve=extend_schema(description="Retrieve a process variable set relationship"),
    update=extend_schema(description="Update a process variable set relationship"),
    partial_update=extend_schema(description="Partially update a process variable set relationship"),
    destroy=extend_schema(description="Delete a process variable set relationship"),
)
class ProcessVariableSetsViewSet(viewsets.ModelViewSet):
    """ViewSet for managing process variable set relationships."""

    queryset = ProcessVariableSets.objects.select_related("process", "variable_set").all()
    serializer_class = ProcessVariableSetsSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["process", "variable_set"]
    search_fields = ["process__code", "variable_set__name"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]


@extend_schema_view(
    list=extend_schema(description="List all file variable set relationships"),
    create=extend_schema(description="Create a new file variable set relationship"),
    retrieve=extend_schema(description="Retrieve a file variable set relationship"),
    update=extend_schema(description="Update a file variable set relationship"),
    partial_update=extend_schema(description="Partially update a file variable set relationship"),
    destroy=extend_schema(description="Delete a file variable set relationship"),
)
class FileVariableSetsViewSet(viewsets.ModelViewSet):
    """ViewSet for managing file variable set relationships."""

    queryset = FileVariableSets.objects.select_related("file", "variable_set").all()
    serializer_class = FileVariableSetsSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["file", "variable_set"]
    search_fields = ["file__code", "variable_set__name"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]
