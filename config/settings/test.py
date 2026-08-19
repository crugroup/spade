"""
With these settings, tests run faster.
"""

from .base import *  # noqa
from .base import env

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="W43r8szRuBzWZfE7xsCRDpagnESYZ0PZyEqYwYTBqEKB0cNaMOS9yFm3aV1NcfmX",
)
# https://docs.djangoproject.com/en/dev/ref/settings/#test-runner
TEST_RUNNER = "django.test.runner.DiscoverRunner"

# PASSWORDS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#password-hashers
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#mailers
MAILERS["default"]["BACKEND"] = "django.core.mail.backends.locmem.EmailBackend"  # noqa: F405

# DEBUGGING FOR TEMPLATES
# ------------------------------------------------------------------------------
TEMPLATES[0]["OPTIONS"]["debug"] = True  # type: ignore # noqa: F405

# STATIC
# ------------------------------------------------------------------------------
# WhiteNoise isn't needed for tests: no staticfiles app installed, no static
# files served, and STATIC_ROOT is never populated (collectstatic only runs
# for production builds).
MIDDLEWARE = [m for m in MIDDLEWARE if m != "whitenoise.middleware.WhiteNoiseMiddleware"]  # noqa: F405

# ------------------------------------------------------------------------------

REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"] = (  # noqa: F405
    "rest_framework_simplejwt.authentication.JWTAuthentication",
    "rest_framework.authentication.SessionAuthentication",
    "rest_framework.authentication.TokenAuthentication",
)
