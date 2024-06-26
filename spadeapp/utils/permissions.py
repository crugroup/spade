from rest_framework.permissions import DjangoModelPermissions


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
