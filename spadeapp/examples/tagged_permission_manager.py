from django.db.models.functions import Lower
from rules.predicates import predicate

from spadeapp.utils.permissions import SpadePermissionManager


@predicate
def tags_intersect_groups(user, obj):
    """
    Predicate that checks if the user's group's names match
    any of the tag names of the object.

    The rules framework also evaluates this with ``obj=None`` for coarse,
    object-less checks (e.g. ``DjangoModelPermissions`` calls ``has_perms``
    without an object). There is no object to compare against in that case, so
    return True and let the object-aware checks (``AutoPermissionViewSetMixin``
    and the list filters) enforce the tag restriction.
    """
    if obj is None:
        return True

    group_names = user.groups.annotate(lower_name=Lower("name")).values("lower_name")
    tag_names = obj.tags.annotate(lower_name=Lower("name")).values("lower_name")
    return group_names.intersection(tag_names).exists()


class TaggedPermissionManager(SpadePermissionManager):
    """
    Example permission manager that manages visibility based on the tags
    of files and processes.

    This manager allows users to view files and processes only if they
    are in a group whose name matches any of the tags of the file/process.
    For example, a user in the group "Sales" would be able to see and use
    all files or processes with the tag "Sales", but no others.
    """

    def __init__(self):
        super().__init__()
        self.add_rule("files.view_file", tags_intersect_groups)
        self.add_rule("files.add_fileupload", tags_intersect_groups)
        self.add_rule("processes.view_process", tags_intersect_groups)
        self.add_rule("processes.add_processrun", tags_intersect_groups)
