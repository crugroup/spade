from dj_rest_auth.views import LogoutView
from django.urls import include, path
from rest_framework import routers
from rest_framework_simplejwt import views as jwt_views

from .views import ObtainTokenView, RegisterUserView, UserProfileView, UserViewSet

router = routers.DefaultRouter()
router.register(r"users", UserViewSet)

app_name = "users"
urlpatterns = [
    path("register/", RegisterUserView.as_view(), name="register"),
    path("token/", jwt_views.TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", jwt_views.TokenRefreshView.as_view(), name="token_refresh"),
    path("users/me/", UserProfileView.as_view(), name="user-me"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("authtoken/", ObtainTokenView.as_view(), name="token_obtain"),
    path("", include(router.urls)),
]
