from rest_framework import serializers
from taggit.serializers import TaggitSerializer, TagListSerializerField

from . import models


class ProcessSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField()

    class Meta:
        model = models.Process
        fields = "__all__"


class ProcessRunParamsSerializer(serializers.Serializer):
    params = serializers.JSONField(required=False)


class ProcessRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProcessRun
        fields = "__all__"


class ExecutorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Executor
        fields = "__all__"

    def validate(self, attrs):
        models.Executor.validate(
            attrs["callable"], attrs.get("history_provider_callable"), serializers.ValidationError
        )
        return attrs
