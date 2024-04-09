from django.conf import settings
from django.contrib.sites.models import Site
from django.db import IntegrityError


def setup_site(sender, **kwargs):
    try:
        Site.objects.update_or_create(
            pk=settings.SITE_ID,
            domain=settings.SITE_DOMAIN,
            name=settings.SITE_NAME,
        )
    # this is only needed for tests
    except IntegrityError:
        pass
