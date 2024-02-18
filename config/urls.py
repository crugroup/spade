from dj_rest_auth.registration.views import VerifyEmailView
from dj_rest_auth.views import PasswordResetConfirmView
from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path("", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path(settings.ADMIN_URL, admin.site.urls),
    path("api/v1/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/v1/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    path("api/v1/", include("spadeapp.users.urls", namespace="api")),
    path("api/", include("spadeapp.files.urls", namespace="files")),
    path("api/", include("spadeapp.processes.urls", namespace="processes")),
    path("api/", include("spadeapp.utils.urls", namespace="utils")),
    re_path(
        r"^api/v1/password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,32})$",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path("api/v1/registration/confirm-email", VerifyEmailView.as_view(), name="account_email_verification_sent"),
    re_path(
        r"api/v1/registration/confirm-email/(?P<key>[-:\w]+)$", VerifyEmailView.as_view(), name="account_confirm_email"
    ),
]
