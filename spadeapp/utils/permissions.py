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
