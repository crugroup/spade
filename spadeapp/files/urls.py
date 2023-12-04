from django.urls import include, path
from rest_framework import routers

from . import api

router = routers.DefaultRouter()

router.register(r"fileformats", api.FileFormatViewSet)
router.register(r"fileprocessors", api.FileProcessorViewSet)
router.register(r"files", api.FileViewSet)
router.register(r"fileuploads", api.FileUploadViewSet)

urlpatterns = [path("v1/", include(router.urls))]

app_name = "files"
