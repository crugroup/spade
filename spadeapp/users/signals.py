from django.conf import settings
from django.contrib.sites.models import Site


def setup_site(sender, **kwargs):
    site = Site.objects.get(pk=settings.SITE_ID)
    site.domain = settings.SITE_DOMAIN
    site.name = settings.SITE_NAME
    site.save()
