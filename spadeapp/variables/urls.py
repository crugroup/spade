from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .api import (
    FileVariableSetsViewSet,
    ProcessVariableSetsViewSet,
    VariableSetViewSet,
    VariableViewSet,
)

app_name = "variables"

router = DefaultRouter()
router.register(r"variables", VariableViewSet)
router.register(r"variable-sets", VariableSetViewSet)
router.register(r"process-variable-sets", ProcessVariableSetsViewSet)
router.register(r"file-variable-sets", FileVariableSetsViewSet)

urlpatterns = [
    path("v1/", include(router.urls)),
]
