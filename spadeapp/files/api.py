from django_filters import rest_framework as filters_drf
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import decorators, parsers, permissions, status, viewsets
from rest_framework.response import Response
from rules.contrib.rest_framework import AutoPermissionViewSetMixin

from ..utils import filters as utils_filters
from ..utils.permissions import PostRequiresViewPermission, filter_visible
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
        viewable_objects = filter_visible(request.user, models.FileFormat.get_perm("view"), queryset)
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
        viewable_objects = filter_visible(request.user, models.FileProcessor.get_perm("view"), queryset)
        serializer = self.get_serializer(viewable_objects, many=True)
        return Response(serializer.data)


class FileViewSet(AutoPermissionViewSetMixin, viewsets.ModelViewSet):
    queryset = models.File.objects.select_related("format", "processor", "linked_process").prefetch_related(
        "tags",
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
        viewable_objects = filter_visible(request.user, models.File.get_perm("view"), queryset)
        serializer = self.get_serializer(viewable_objects, many=True)
        return Response(serializer.data)

    @extend_schema(
        request={"*/*": serializers.FileContentSerializer},
        parameters=[
            OpenApiParameter(name="filename", description="Filename", required=True, type=str),
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

        serializer = serializers.FileUploadSerializer(
            run := service.FileService.process_file(
                file=file,
                data=request.data["file"].read(),
                filename=request.data["filename"],
                user=request.user,
                user_params=request.data.get("params"),
            )
        )

        return Response(
            status=status.HTTP_200_OK if run.result != "failed" else status.HTTP_400_BAD_REQUEST, data=serializer.data
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

    def get_queryset(self):
        # An upload is only visible when its file is visible to the user.
        user = self.request.user
        visible_files = filter_visible(user, models.File.get_perm("view"), models.File.objects.all())
        queryset = super().get_queryset().filter(file__in=visible_files)
        if self.action == "list":
            # Detail actions keep the upload's own view rule in AutoPermissionViewSetMixin (403, not 404).
            queryset = filter_visible(user, models.FileUpload.get_perm("view"), queryset)
        return queryset

    def list(self, request, *args, **kwargs) -> Response:
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
