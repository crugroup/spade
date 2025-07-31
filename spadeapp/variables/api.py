from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

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

    def update(self, request, *args, **kwargs):
        """Override update to prevent modification of is_secret field after creation."""
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        # Remove is_secret from request data if it's different from the instance
        if "is_secret" in request.data and request.data["is_secret"] != instance.is_secret:
            return Response(
                {
                    "detail": "The 'is_secret' field cannot be modified after creation. "
                    "Delete and recreate the variable to change this property."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class VariableSetViewSet(viewsets.ModelViewSet):
    """ViewSet for managing variable sets."""

    queryset = VariableSet.objects.prefetch_related("variables").all()
    serializer_class = VariableSetSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at", "updated_at"]
    ordering = ["name"]
