from rest_framework import serializers
from taggit.serializers import TaggitSerializer, TagListSerializerField

from . import models


class FileFormatSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FileFormat
        fields = "__all__"


class FileContentSerializer(serializers.Serializer):
    file = serializers.FileField(required=True)


class FileProcessorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FileProcessor
        fields = "__all__"

    def validate(self, attrs):
        models.FileProcessor.validate(attrs["callable"], serializers.ValidationError)
        return attrs


class FileSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField()

    class Meta:
        model = models.File
        fields = "__all__"


class FileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FileUpload
        fields = "__all__"
