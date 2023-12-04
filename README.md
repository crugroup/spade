# Spade

Simplicity at its best.

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)
[![Black code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)


## Basic Commands

### Setting Up Your Users

- To create a **normal user account**, just go to Sign Up and fill out the form. Once you submit it, you'll see a "Verify Your E-mail Address" page. Go to your console to see a simulated email verification message. Copy the link into your browser. Now the user's email should be verified and ready to go.

- To create a **superuser account**, use this command:

      $ python manage.py createsuperuser


### Type checks

Running type checks with mypy:

    $ mypy spadeapp

### Test coverage

To run the tests, check your test coverage, and generate an HTML coverage report:

    $ coverage run -m pytest
    $ coverage html
    $ open htmlcov/index.html

#### Running tests with pytest

    $ pytest


## Development

### Local development - only Postgres in Docker

Install local dependencies

```
pip install -r requirements/local.txt
```

Run your a local django server

```
export DJANGO_READ_DOT_ENV_FILE=True
export DJANGO_ENV_FILE=.envs/.local/.local
docker-compose -f local.yml up -d postgres
./manage.py runserver

```
