from django.urls import include, path
from rest_framework import routers

from . import api

router = routers.DefaultRouter()

router.register(r"processes", api.ProcessViewSet)
router.register(r"processruns", api.ProcessRunViewSet)
router.register(r"executors", api.ExecutorViewSet)


urlpatterns = [path("v1/", include(router.urls))]

app_name = "files"
