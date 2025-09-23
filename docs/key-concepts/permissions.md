---
sidebar_position: 6
---

# Permissions

Permissions in Spade are controlled using the `SpadePermissionManager` class, which holds rules that apply to each action a user can take in the API.

These rules are defined as predicates using the `rules` library. Each predicate is given the user object making the request, and the object they are trying to interact with. An example predicate might look something like this:

```py
from rules.predicates import predicate

@predicate
def user_is_adult(user, obj):
    return user.age >= 18
```

To make use of these rules, one can create a subclass of `SpadePermissionManager` and reference its code using the Django config setting `SPADE_PERMISSION_MANAGER`. The code needs to be installed into the same environment as Spade, and is specified as an import to the class. An example might be:

```bash
SPADE_PERMISSION_MANAGER="spadeapp.examples.tagged_permission_manager.TaggedPermissionManager"
```

A declaration for a permissions class would look something like:

```py
class MyPermissionManager(SpadePermissionManager):
    def __init__(self):
        super().__init__()
        self.add_rule("files.view_file", user_is_adult)
        self.add_rule("processes.view_process", user_is_adult)
```

Once installed and configured, these rules will then run on each call to the API and only allow the request to run if the given predicate returns True. In the example above, this would mean that viewing any file uploads or processes will be blocked if the user object's age is not 18 or above.

As all of the inputs are regular Django objects, one can also construct querysets in order to fulfill more complex logic. For example, in the `TaggedPermissionManager` object defined in the examples folder, the following predicate will only pass if there is any overlap between the tags of an objects and the user's groups:

```py
@predicate
def tags_intersect_groups(user, obj):
    """
    Predicate that checks if the user's group's names match
    any of the tag names of the object.
    """
    group_names = user.groups.annotate(lower_name=Lower("name")).values("lower_name")
    tag_names = obj.tags.annotate(lower_name=Lower("name")).values("lower_name")
    return group_names.intersection(tag_names).exists()
```

A `default_rule` predicate can also be specified in the manager class, which will run for all permissions where there is not a rule explicitly set for it. By default, this rule is set to `rules.always_allow`.
