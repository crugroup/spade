from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .api import (
    VariableSetViewSet,
    VariableViewSet,
)

app_name = "variables"

router = DefaultRouter(trailing_slash=False)
router.register(r"variables", VariableViewSet)
router.register(r"variable-sets", VariableSetViewSet)

urlpatterns = [
    path("v1/", include(router.urls)),
]
