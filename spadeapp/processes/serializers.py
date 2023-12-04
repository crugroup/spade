from rest_framework import serializers

from . import models


class ProcessSerializer(serializers.ModelSerializer):
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
