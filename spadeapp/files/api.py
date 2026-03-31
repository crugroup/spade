from django_filters import rest_framework as filters_drf
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import decorators, parsers, permissions, status, viewsets
from rest_framework.response import Response
from rules.contrib.rest_framework import AutoPermissionViewSetMixin

from ..processes import models as process_models
from ..utils import filters as utils_filters
from ..utils.permissions import PostRequiresViewPermission
from . import models, serializers, service


class FileFilterSet(filters_drf.FilterSet):
    tags = utils_filters.TagsFilter()

    class Meta:
        model = models.File
        fields = ("tags", "code", "format", "processor")


class FileFormatViewSet(AutoPermissionViewSetMixin, viewsets.ModelViewSet):
    queryset = models.FileFormat.objects.all()
    serializer_class = serializers.FileFormatSerializer
    permission_classes = [permissions.DjangoModelPermissions]
    filterset_fields = ("format",)

    permission_type_map = {
        **AutoPermissionViewSetMixin.permission_type_map,
        "list": "list",
    }

    def list(self, request, *args, **kwargs) -> Response:
        queryset = self.filter_queryset(self.get_queryset())
        viewable_objects = filter(
            lambda obj: request.user.has_perm(models.FileFormat.get_perm("view"), obj),
            queryset,
        )
        serializer = self.get_serializer(viewable_objects, many=True)
        return Response(serializer.data)


class FileProcessorViewSet(AutoPermissionViewSetMixin, viewsets.ModelViewSet):
    queryset = models.FileProcessor.objects.all()
    serializer_class = serializers.FileProcessorSerializer
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
            lambda obj: request.user.has_perm(models.FileProcessor.get_perm("view"), obj),
            queryset,
        )
        serializer = self.get_serializer(viewable_objects, many=True)
        return Response(serializer.data)


class FileViewSet(AutoPermissionViewSetMixin, viewsets.ModelViewSet):
    queryset = models.File.objects.select_related("format", "processor", "linked_process").prefetch_related(
        "tags",
        "one_move_links__process",
        "variable_sets__variables",
    )
    serializer_class = serializers.FileSerializer
    permission_classes = [permissions.DjangoModelPermissions]
    filterset_class = FileFilterSet
    search_fields = ("code", "description")

    permission_type_map = {
        **AutoPermissionViewSetMixin.permission_type_map,
        "list": "list",
        "upload": "upload",
    }

    def list(self, request, *args, **kwargs) -> Response:
        queryset = self.filter_queryset(self.get_queryset())
        viewable_objects = filter(
            lambda obj: request.user.has_perm(models.File.get_perm("view"), obj),
            queryset,
        )
        serializer = self.get_serializer(viewable_objects, many=True)
        return Response(serializer.data)

    @extend_schema(
        request={"*/*": serializers.FileContentSerializer},
        parameters=[
            OpenApiParameter(name="filename", description="Filename", required=True, type=str),
            OpenApiParameter(
                name="process_id",
                description=(
                    "Optional process to run after a successful upload. OneMove can supply "
                    "this to start a selected process; defaults to the file's legacy linked process."
                ),
                required=False,
                type=int,
            ),
            OpenApiParameter(
                name="run_linked_process",
                description="Whether to run the linked process after upload. Defaults to true.",
                required=False,
                type=bool,
            ),
        ],
        responses={200: serializers.FileUploadSerializer},
    )
    @decorators.action(
        detail=True,
        methods=["post"],
        parser_classes=[parsers.MultiPartParser, parsers.FileUploadParser],
        permission_classes=[PostRequiresViewPermission],
    )
    def upload(self, request, pk, format=None):
        file = self.get_object()
        linked_process = None
        run_linked_process = str(request.data.get("run_linked_process", "true")).lower() not in ("false", "0", "no")

        process_id = request.data.get("process_id")
        if process_id not in (None, ""):
            try:
                process_id = int(process_id)
            except (TypeError, ValueError):
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={"error_message": "process_id must be an integer"},
                )

            linked_process = process_models.Process.objects.filter(pk=process_id).first()
            if linked_process is None:
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={"error_message": "Selected process does not exist"},
                )

            if not file.is_available_for_one_move_process(linked_process):
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={"error_message": "Selected process is not linked to this file"},
                )

            if not request.user.has_perm(process_models.Process.get_perm("view"), linked_process):
                return Response(
                    status=status.HTTP_403_FORBIDDEN,
                    data={"detail": "You do not have access to that process"},
                )

        serializer = serializers.FileUploadSerializer(
            run := service.FileService.process_file(
                file=file,
                upload_payload={
                    "data": request.data["file"].read(),
                    "filename": request.data["filename"],
                    "user_params": request.data.get("params"),
                },
                user=request.user,
                linked_process=linked_process,
                run_linked_process=run_linked_process,
            )
        )

        return Response(
            status=(status.HTTP_200_OK if run.result != "failed" else status.HTTP_400_BAD_REQUEST),
            data=serializer.data,
        )


class FileUploadViewSet(AutoPermissionViewSetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = models.FileUpload.objects.select_related("file", "user", "linked_process_run")
    serializer_class = serializers.FileUploadSerializer
    permission_classes = [permissions.DjangoModelPermissions]
    filterset_fields = (
        "id",
        "file",
        "name",
        "size",
        "rows",
        "result",
        "user",
        "created_at",
    )

    permission_type_map = {
        **AutoPermissionViewSetMixin.permission_type_map,
        "list": "list",
    }

    def list(self, request, *args, **kwargs) -> Response:
        queryset = self.filter_queryset(self.get_queryset())
        viewable_objects = filter(
            lambda obj: request.user.has_perm(models.FileUpload.get_perm("view"), obj),
            queryset,
        )
        serializer = self.get_serializer(viewable_objects, many=True)
        return Response(serializer.data)
