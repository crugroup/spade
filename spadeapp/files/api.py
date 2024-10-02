from django_filters import rest_framework as filters_drf
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import decorators, parsers, permissions, status, viewsets
from rest_framework.response import Response
from rules.contrib.rest_framework import AutoPermissionViewSetMixin

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
    filterset_fields = "__all__"

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
    queryset = models.File.objects.all()
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
            service.FileService.process_file(
                file=file,
                data=request.data["file"].read(),
                filename=request.data["filename"],
                user=request.user,
                user_params=request.data.get("params"),
            )
        )

        return Response(status=status.HTTP_200_OK, data=serializer.data)


class FileUploadViewSet(AutoPermissionViewSetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = models.FileUpload.objects.all()
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
