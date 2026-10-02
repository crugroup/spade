from rest_framework import serializers
from taggit.serializers import TaggitSerializer, TagListSerializerField

from . import models


class ProcessSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField(required=False)
    latest_run = serializers.SerializerMethodField()

    class Meta:
        model = models.Process
        fields = "__all__"

    def get_latest_run(self, obj):
        # Kept for API compatibility; clients load latest runs in bulk from ``/processes/latest_runs``.
        return None


class ProcessRunParamsSerializer(serializers.Serializer):
    params = serializers.JSONField(required=False)


class ProcessRunSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(source="user_id", allow_null=True, read_only=True)

    class Meta:
        model = models.ProcessRun
        fields = "__all__"


class ProcessLatestRunSerializer(serializers.Serializer):
    process_id = serializers.IntegerField()
    latest_run = ProcessRunSerializer(allow_null=True)


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
