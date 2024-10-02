---
sidebar_position: 5
---

# User
A **User** is a simple dataclass representing the Spade user currently executing the given [Executor](executor.md) or [File Processor](file-processor.md).

The object is created and filled in with user data whenever the `run`/`process` methods are executed.

It consists of the following attributes:
* `id` (int)
* `email` (str)
* `first_name` (str)
* `last_name` (str)

No editing of the user's attributes can be done via this object - it is simply a copy of the User's information.
