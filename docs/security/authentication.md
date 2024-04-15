---
sidebar_position: 1
---

# Authentication

The initial version of Spade supports username and password authentication. We plan to add more authentication methods in the future.

# User management

## Creating as superuser

Depending on the value of the `DJANGO_ACCOUNT_FIRST_USER_ADMIN` environment variable (defaults to `True`), the first user created will be a superuser or a regular user. The superuser can create other users and assign them roles.

You can also create a superuser by running the following command:

```bash
./manage.py createsuperuser
```

Inside the docker the container it is:

```bash
/entrpoint /app/manage.py createsuperuser
```

Or if you use docker compose

```bash
docker-compose exec spade /app/manage.py createsuperuser
```

## Creating users

At present there are two ways to create users:
* Using the Django admin interface, available at `/admin`
* Allowing users to register themselves, by setting the `DJANGO_ACCOUNT_ALLOW_REGISTRATION` environment variable to `True` (defaults to `True`)

### JWT token

You can call `api/v1/token` to get a JWT token, which can next be used to interact directly with spade APIs.
Full Swagger API documentation is available at `/` of Spade backend for authenticated users.