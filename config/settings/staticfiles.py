"""
Minimal settings in order to collect static files during build.
"""

from .base import *  # noqa

# STATIC
# ------------------------
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
# MEDIA
# ------------------------------------------------------------------------------
INSTALLED_APPS = ["django.contrib.staticfiles"] + INSTALLED_APPS  # noqa: F405
