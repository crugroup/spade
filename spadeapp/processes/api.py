from django_filters import rest_framework as filters_drf
from drf_spectacular.utils import extend_schema
from rest_framework import decorators, permissions, status, viewsets
from rest_framework.response import Response
from rules.contrib.rest_framework import AutoPermissionViewSetMixin

from ..utils import filters as utils_filters
from ..utils.permissions import PostRequiresViewPermission
from . import models, serializers, service


class ProcessFilterSet(filters_drf.FilterSet):
    tags = utils_filters.TagsFilter()

    class Meta:
        model = models.Process
        fields = ("tags", "code", "executor")


class ProcessViewSet(AutoPermissionViewSetMixin, viewsets.ModelViewSet):
    queryset = models.Process.objects.all()
    serializer_class = serializers.ProcessSerializer
    permission_classes = [permissions.DjangoModelPermissions]
    filterset_class = ProcessFilterSet
    search_fields = ("code", "description")

    permission_type_map = {
        **AutoPermissionViewSetMixin.permission_type_map,
        "list": "list",
        "run": "run",
    }

    def list(self, request, *args, **kwargs) -> Response:
        queryset = self.filter_queryset(self.get_queryset())
        viewable_objects = filter(
            lambda obj: request.user.has_perm(models.Process.get_perm("view"), obj),
            queryset,
        )
        serializer = self.get_serializer(viewable_objects, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=serializers.ProcessRunParamsSerializer,
        responses={
            200: serializers.ProcessRunSerializer,
            500: serializers.ProcessRunSerializer,
        },
    )
    @decorators.action(detail=True, methods=["post"], permission_classes=[PostRequiresViewPermission])
    def run(self, request, pk):
        process = self.get_object()
        serializer = serializers.ProcessRunSerializer(
            run := service.ProcessService.run_process(process, request.user, request.data["params"])
        )

        return Response(
            status=status.HTTP_200_OK if run.status != "error" else status.HTTP_500_INTERNAL_SERVER_ERROR,
            data=serializer.data,
        )


class ProcessRunViewSet(AutoPermissionViewSetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = models.ProcessRun.objects.all()
    serializer_class = serializers.ProcessRunSerializer
    permission_classes = [permissions.DjangoModelPermissions]
    filterset_fields = (
        "id",
        "process",
        "user",
        "status",
        "result",
        "created_at",
    )

    permission_type_map = {
        **AutoPermissionViewSetMixin.permission_type_map,
        "list": "list",
    }

    def list(self, request, *args, **kwargs):
        process_id = self.request.query_params.get("process", None)
        if not process_id:
            return super().list(request, *args, **kwargs)

        try:
            process = models.Process.objects.get(id=process_id)
        except models.Process.DoesNotExist:
            return Response([])

        runs = service.ProcessService.get_runs(process, request, *args, **kwargs)
        runs = filter(
            lambda obj: request.user.has_perm(models.ProcessRun.get_perm("view"), obj),
            runs,
        )

        serializer = serializers.ProcessRunSerializer(runs, many=True)

        return Response(serializer.data)


class ExecutorViewSet(AutoPermissionViewSetMixin, viewsets.ModelViewSet):
    queryset = models.Executor.objects.all()
    serializer_class = serializers.ExecutorSerializer
    permission_classes = [permissions.DjangoModelPermissions]
    filterset_fields = "__all__"
    search_fields = ("name", "description")

    permission_type_map = {
        **AutoPermissionViewSetMixin.permission_type_map,
        "list": "list",
    }

    def list(self, request, *args, **kwargs) -> Response:
        queryset = self.filter_queryset(self.get_queryset())
        viewable_objects = filter(
            lambda obj: request.user.has_perm(models.Executor.get_perm("view"), obj),
            queryset,
        )
        serializer = self.get_serializer(viewable_objects, many=True)
        return Response(serializer.data)
