from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    name = "spadeapp.users"
    verbose_name = _("Users")

    def ready(self):
        try:
            import spadeapp.users.signals  # noqa: F401

            post_migrate.connect(spadeapp.users.signals.setup_site, sender=self)
        except ImportError:
            pass
