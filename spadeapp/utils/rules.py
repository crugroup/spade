from django.conf import settings
from rules.predicates import predicate


def defer_rule(name):
    @predicate
    def wrapper(*args):
        return settings.SPADE_PERMISSIONS.test_rule(name, *args)

    return wrapper
