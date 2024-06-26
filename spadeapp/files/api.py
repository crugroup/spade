from django_filters import rest_framework as filters_drf
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import decorators, parsers, permissions, status, viewsets
from rest_framework.response import Response

from ..utils import filters as utils_filters
from . import models, serializers, service


class FileFilterSet(filters_drf.FilterSet):
    tags = utils_filters.TagsFilter()

    class Meta:
        model = models.File
        fields = ("tags", "code", "format", "processor")


class FileFormatViewSet(viewsets.ModelViewSet):
    queryset = models.FileFormat.objects.all()
    serializer_class = serializers.FileFormatSerializer
    permission_classes = [permissions.DjangoModelPermissions]
    filterset_fields = "__all__"


class FileProcessorViewSet(viewsets.ModelViewSet):
    queryset = models.FileProcessor.objects.all()
    serializer_class = serializers.FileProcessorSerializer
    permission_classes = [permissions.DjangoModelPermissions]
    filterset_fields = "__all__"
    search_fields = ("name", "description")


class FileViewSet(viewsets.ModelViewSet):
    queryset = models.File.objects.all()
    serializer_class = serializers.FileSerializer
    permission_classes = [permissions.DjangoModelPermissions]
    filterset_class = FileFilterSet
    search_fields = ("code", "description")

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


class FileUploadViewSet(viewsets.ReadOnlyModelViewSet):
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
