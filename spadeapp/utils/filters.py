from django_filters import rest_framework as filters


class TagsFilter(filters.CharFilter):
    def filter(self, qs, value):
        if value:
            qs = qs.filter(tags__name__in=[value])

        return qs
