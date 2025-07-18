# Spade

**Simplicity at its best.**

**Project page**: [getspade.io](https://getspade.io)

**Documentation** [crugroup.github.io/spade](https://crugroup.github.io/spade/)

## Quick Start

```bash
curl -O https://crugroup.github.io/spade/docker-compose.yml
docker compose up
```

## Development

### Local development - only Postgres in Docker

Install local dependencies

```
pip install -r requirements/local.txt
```

Start a local postgres server in Docker

```
export DJANGO_READ_DOT_ENV_FILE=True
export DJANGO_ENV_FILE=.envs/.local/.local
docker-compose -f local.yml up -d postgres

```

### Running a local server
```
./manage.py runserver
```


### Setting Up Your Users

- To create a **normal user account**, just go to Sign Up and fill out the form.
  Once you submit it, you'll see a "Verify Your E-mail Address" page.
  Go to your console to see a simulated email verification message.
  Copy the link into your browser. Now the user's email should be verified and ready to go.
  Some things to note about accounts:
  - The first created user is automatically a Superuser.

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

## Examples

`spadeapp.examples` contains some examples for basic objects such as executor, processor, and history provider.
