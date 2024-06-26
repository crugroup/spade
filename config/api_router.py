from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from spadeapp.users.api.views import UserViewSet

if settings.DEBUG:
    router = DefaultRouter(trailing_slash=False)
else:
    router = SimpleRouter(trailing_slash=False)

router.register("users", UserViewSet)


app_name = "api"
urlpatterns = router.urls
