from rest_framework import viewsets
from taggit.models import Tag

from .serializers import TagSerializer


class TagViewSet(viewsets.ModelViewSet):
    """
    Not using taggit_serializer.serializers.TaggitSerializer because that's for listing
    tags for an instance of a model
    """

    queryset = Tag.objects.all().order_by("name")
    serializer_class = TagSerializer
