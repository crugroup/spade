from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from .models import Variable, VariableSet
from .serializers import (
    VariableSerializer,
    VariableSetSerializer,
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


class VariableSetViewSet(viewsets.ModelViewSet):
    """ViewSet for managing variable sets."""

    queryset = VariableSet.objects.prefetch_related("variables").all()
    serializer_class = VariableSetSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at", "updated_at"]
    ordering = ["name"]
