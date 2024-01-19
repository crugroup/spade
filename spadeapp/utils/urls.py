from django.urls import include, path
from rest_framework import routers

from . import api

router = routers.DefaultRouter(trailing_slash=False)

router.register(r"tags", api.TagViewSet)


urlpatterns = [path("v1/", include(router.urls))]

app_name = "utils"
