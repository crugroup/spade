from rest_framework import serializers
from taggit.serializers import TaggitSerializer, TagListSerializerField

from . import models
from .service import ProcessService


class ProcessSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField(required=False)
    latest_run = serializers.SerializerMethodField()

    class Meta:
        model = models.Process
        fields = "__all__"

    def get_latest_run(self, obj):
        request = self.context.get("request")
        if request is None:
            return None

        latest_run = next(iter(ProcessService.get_runs(obj, request)), None)
        if latest_run is None:
            return None

        return ProcessRunSerializer(latest_run).data


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
            attrs["callable"],
            attrs.get("history_provider_callable"),
            serializers.ValidationError,
        )
        return attrs
