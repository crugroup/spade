from django.conf import settings
from django.contrib.sites.models import Site


def setup_site(sender, **kwargs):
    Site.objects.update_or_create(
        pk=settings.SITE_ID,
        domain=settings.SITE_DOMAIN,
        name=settings.SITE_NAME,
    )
