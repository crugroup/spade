import rules
from django.conf import settings
from rest_framework.permissions import DjangoModelPermissions
from rules.predicates import predicate

from .imports import import_object


class PostRequiresViewPermission(DjangoModelPermissions):
    """
    Custom permission class that uses the view permission for post requests

    Used for the file upload and process run actions, as by default post
    requires the create permission
    """

    perms_map = {
        **DjangoModelPermissions.perms_map,
        "POST": ["%(app_label)s.view_%(model_name)s"],
    }


class SpadePermissionManager:
    default_rule = rules.always_allow

    def __init__(self):
        self.rules = {}

    def add_rule(self, name, rule):
        self.rules[name] = rule

    def test_rule(self, name, *args):
        return self.rules.get(name, self.default_rule).test(*args)

    def filter_visible(self, name, user, queryset):
        """
        Return the objects in ``queryset`` for which ``user`` passes rule ``name``.

        Mirrors ``user.has_perm(name, obj)`` for every object: inactive users see
        nothing and superusers see everything. Allow-all and deny-all rules are
        resolved without touching the database; any other rule is tested per object.
        Subclasses can override ``filter_by_rule`` to express a rule as a database filter.
        """
        if not user.is_active:
            return queryset.none()
        if user.is_superuser:
            return queryset

        rule = self.rules.get(name, self.default_rule)
        if rule is rules.always_allow:
            return queryset
        if rule is rules.always_deny:
            return queryset.none()
        return self.filter_by_rule(rule, user, queryset)

    def filter_by_rule(self, rule, user, queryset):
        """Fallback: evaluate ``rule`` for each object in Python."""
        return queryset.filter(pk__in=[obj.pk for obj in queryset if rule.test(user, obj)])


class PermissionManagerCache:
    def __init__(self):
        self.cache = {}

    def get_manager(self) -> SpadePermissionManager:
        name = settings.SPADE_PERMISSION_MANAGER
        if name not in self.cache:
            self.cache[name] = import_object(name)()

        return self.cache[name]


permission_manager_cache = PermissionManagerCache()


def defer_rule(name):
    @predicate
    def wrapper(*args):
        return permission_manager_cache.get_manager().test_rule(name, *args)

    return wrapper


def filter_visible(user, perm, queryset):
    """Filter ``queryset`` to the objects ``user`` has object permission ``perm`` on."""
    return permission_manager_cache.get_manager().filter_visible(perm, user, queryset)
