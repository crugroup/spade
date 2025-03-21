from dj_rest_auth.registration.views import ResendEmailVerificationView
from dj_rest_auth.views import LogoutView, PasswordChangeView, PasswordResetView
from django.urls import include, path
from rest_framework import routers
from rest_framework_simplejwt import views as jwt_views

from .views import (
    GroupViewSet,
    ObtainTokenView,
    PermissionsView,
    RegisterUserView,
    UserPermissionsView,
    UserProfileView,
    UserViewSet,
)

router = routers.DefaultRouter(trailing_slash=False)
router.register(r"users", UserViewSet)
router.register(r"groups", GroupViewSet)

app_name = "users"
urlpatterns = [
    path("registration", RegisterUserView.as_view(), name="register"),
    path(
        "registration/resend-verification-email",
        ResendEmailVerificationView.as_view(),
        name="resend-confirmation-email",
    ),
    path("token", jwt_views.TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh", jwt_views.TokenRefreshView.as_view(), name="token_refresh"),
    path("users/me", UserProfileView.as_view(), name="user-me"),
    path("logout", LogoutView.as_view(), name="logout"),
    path("authtoken", ObtainTokenView.as_view(), name="token_obtain"),
    path("password/reset", PasswordResetView.as_view(), name="password_reset"),
    path("password/change", PasswordChangeView.as_view(), name="password_change"),
    path("users/me/permissions", UserPermissionsView.as_view(), name="user_permissions"),
    path("permissions", PermissionsView.as_view(), name="permissions"),
    path("", include(router.urls)),
]
