from django.db.models import QuerySet
from django_filters import rest_framework as filters_drf
from drf_spectacular.utils import extend_schema
from rest_framework import decorators, permissions, status, viewsets
from rest_framework.response import Response
from rules.contrib.rest_framework import AutoPermissionViewSetMixin

from ..utils import filters as utils_filters
from ..utils.permissions import PostRequiresViewPermission, filter_visible
from . import models, serializers, service


class ProcessFilterSet(filters_drf.FilterSet):
    tags = utils_filters.TagsFilter()

    class Meta:
        model = models.Process
        fields = ("tags", "code", "executor")


class ProcessViewSet(AutoPermissionViewSetMixin, viewsets.ModelViewSet):
    queryset = models.Process.objects.select_related("executor").prefetch_related("tags", "variable_sets__variables")
    serializer_class = serializers.ProcessSerializer
    permission_classes = [permissions.DjangoModelPermissions]
    filterset_class = ProcessFilterSet
    search_fields = ("code", "description")

    permission_type_map = {
        **AutoPermissionViewSetMixin.permission_type_map,
        "list": "list",
        "latest_runs": "list",
        "run": "run",
    }

    def list(self, request, *args, **kwargs) -> Response:
        queryset = self.filter_queryset(self.get_queryset())
        viewable_objects = filter_visible(request.user, models.Process.get_perm("view"), queryset)
        serializer = self.get_serializer(viewable_objects, many=True)
        return Response(serializer.data)

    @extend_schema(
        responses={200: serializers.ProcessLatestRunSerializer(many=True)},
    )
    @decorators.action(detail=False, methods=["get"])
    def latest_runs(self, request, *args, **kwargs) -> Response:
        queryset = self.filter_queryset(self.get_queryset())
        ids_param = request.query_params.get("ids")
        if ids_param:
            requested_ids = {int(value) for value in ids_param.split(",") if value.strip().isdigit()}
            queryset = queryset.filter(id__in=requested_ids)

        viewable_objects = list(filter_visible(request.user, models.Process.get_perm("view"), queryset))
        latest_runs_by_process_id = service.ProcessService.get_latest_runs_for_processes(viewable_objects, request)
        # Apply the run's own view rule on both the cached and the freshly queried path.
        # A hidden latest run is reported as no run rather than falling back to an older one.
        view_run_perm = models.ProcessRun.get_perm("view")
        payload = [
            {
                "process_id": process.id,
                "latest_run": latest_run
                if (latest_run := latest_runs_by_process_id.get(process.id)) is not None
                and request.user.has_perm(view_run_perm, latest_run)
                else None,
            }
            for process in viewable_objects
        ]

        serializer = serializers.ProcessLatestRunSerializer(payload, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=serializers.ProcessRunParamsSerializer,
        responses={
            200: serializers.ProcessRunSerializer,
            400: serializers.ProcessRunSerializer,
        },
    )
    @decorators.action(detail=True, methods=["post"], permission_classes=[PostRequiresViewPermission])
    def run(self, request, pk):
        process = self.get_object()
        serializer = serializers.ProcessRunSerializer(
            run := service.ProcessService.run_process(process, request.user, request.data.get("params"))
        )

        return Response(
            status=status.HTTP_200_OK
            if run.status not in ("failed", models.ProcessRun.Statuses.ERROR)
            else status.HTTP_400_BAD_REQUEST,
            data=serializer.data,
        )


class ProcessRunViewSet(AutoPermissionViewSetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = models.ProcessRun.objects.select_related("process", "user")
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

    def get_queryset(self):
        # A run is only visible when its process is visible to the user.
        user = self.request.user
        visible_processes = filter_visible(user, models.Process.get_perm("view"), models.Process.objects.all())
        queryset = super().get_queryset().filter(process__in=visible_processes)
        if self.action == "list":
            # Detail actions keep the run's own view rule in AutoPermissionViewSetMixin (403, not 404).
            queryset = filter_visible(user, models.ProcessRun.get_perm("view"), queryset)
        return queryset

    def list(self, request, *args, **kwargs):
        process_id = self.request.query_params.get("process", None)
        if not process_id:
            return super().list(request, *args, **kwargs)

        try:
            process_id = int(process_id)
        except ValueError:
            return Response({"process": ["A valid integer is required."]}, status=status.HTTP_400_BAD_REQUEST)

        try:
            process = (
                models.Process.objects.select_related("executor")
                .prefetch_related("variable_sets__variables")
                .get(id=process_id)
            )
        except models.Process.DoesNotExist:
            process = None

        if process is None or not request.user.has_perm(models.Process.get_perm("view"), process):
            return self.get_paginated_response(self.paginate_queryset([]))

        runs = service.ProcessService.get_runs(process, request, *args, **kwargs)
        if isinstance(runs, QuerySet):
            # Local history: filter in the database, which also applies the visibility rules
            # and the remaining query filters (status, user, ...).
            runs = self.filter_queryset(self.get_queryset()).filter(process=process)
        else:
            view_run_perm = models.ProcessRun.get_perm("view")
            runs = [run for run in runs if request.user.has_perm(view_run_perm, run)]

        page = self.paginate_queryset(runs)
        serializer = serializers.ProcessRunSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)


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
        viewable_objects = filter_visible(request.user, models.Executor.get_perm("view"), queryset)
        serializer = self.get_serializer(viewable_objects, many=True)
        return Response(serializer.data)
