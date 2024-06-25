from .base import *  # noqa
from .base import env, SPADE_PERMISSIONS
import rules

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = True
# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="iL7YxAEjpx4ry1SK2St4TSTMg0QdZzXVoJKRe8QXoPJ8As13jwqAeIaWstHbEvKG",
)
# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ["localhost", "0.0.0.0", "127.0.0.1"]

# CACHES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#caches
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "",
    }
}

# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = env("DJANGO_EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")

# WhiteNoise
# ------------------------------------------------------------------------------
# http://whitenoise.evans.io/en/latest/django.html#using-whitenoise-in-development
INSTALLED_APPS = ["whitenoise.runserver_nostatic"] + INSTALLED_APPS  # noqa: F405


# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#internal-ips
INTERNAL_IPS = ["127.0.0.1", "10.0.2.2"]
if env("USE_DOCKER") == "yes":
    import socket

    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS += [".".join(ip.split(".")[:-1] + ["1"]) for ip in ips]

# django-extensions
# ------------------------------------------------------------------------------
# https://django-extensions.readthedocs.io/en/latest/installation_instructions.html#configuration
INSTALLED_APPS += ["django_extensions"]  # noqa: F405

REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"] = (  # noqa: F405
    "rest_framework_simplejwt.authentication.JWTAuthentication",
    "rest_framework.authentication.SessionAuthentication",
    "rest_framework.authentication.TokenAuthentication",
)

CORS_ALLOWED_ORIGINS += ["http://localhost:5173"]  # noqa: F405


# RULES
# ------------------------------------------------------------------------------


# Predicate that checks if the group names of a user match
# any of the tags of the given object
@rules.predicate
def groups_match_tags(user, obj):
    if user.is_superuser:
        return True
    group_names = user.groups.values("name")
    tag_names = obj.tags.values("name")
    return group_names.intersection(tag_names).exists()


SPADE_PERMISSIONS.set_rule("files.view_file", groups_match_tags)
SPADE_PERMISSIONS.set_rule("files.upload_file", groups_match_tags)
SPADE_PERMISSIONS.set_rule("processes.view_process", groups_match_tags)
SPADE_PERMISSIONS.set_rule("processes.run_process", groups_match_tags)
