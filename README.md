# Spade

**Simplicity at its best.**

**Project page**: [getspade.io](https://getspade.io)

**Documentation** [crugroup.github.io/spade](https://crugroup.github.io/spade/)

## Quick Start

```bash
curl -O https://crugroup.github.io/spade/docker-compose.yml
docker compose up
```

## Your files own files and processes

To support your own set of files and processes you'll use **Spade SDK**.

For more details see the [Spade SDK docs](https://crugroup.github.io/spade/docs/key-concepts/spade-sdk)

## Spade development

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

## Maintenance

### Docker-based development (recommended)

#### Prerequisites
- Docker & Docker Compose
- Pre-commit (install with `pip install pre-commit`)

#### Start all services
```bash
docker compose -f local.yml up -d
```
Starts Django, PostgreSQL, and SpadeUI containers.
- Django API: `http://localhost:8081`
- PostgreSQL: port 5432
- SpadeUI: `http://localhost:3000`

#### View logs
```bash
docker compose -f local.yml logs -f django
docker compose -f local.yml logs -f postgres
```

#### Stop services
```bash
docker compose -f local.yml down
```

### Testing

#### Run all tests
```bash
docker compose -f local.yml run --rm django pytest -v
```
Expected: 47 tests passing in < 1 second.

#### Run specific test file
```bash
docker compose -f local.yml run --rm django pytest spadeapp/users/tests/test_models.py -v
```

#### Run with coverage
```bash
docker compose -f local.yml run --rm django coverage run -m pytest
docker compose -f local.yml run --rm django coverage report
docker compose -f local.yml run --rm django coverage html
```

### Code Quality

#### Run pre-commit hooks
```bash
pre-commit run --all-files
```
Runs 16 hooks: ruff (linter), black (formatter), django-upgrade, djlint, etc.

#### Install pre-commit hooks
```bash
pre-commit install
```
Auto-runs hooks on every commit.

#### Manual linting
```bash
docker compose -f local.yml run --rm django ruff check .
docker compose -f local.yml run --rm django black --check .
```

### Database Management

#### Check migrations
```bash
docker compose -f local.yml run --rm django python manage.py showmigrations
```

#### Create migrations
```bash
docker compose -f local.yml run --rm django python manage.py makemigrations
```

#### Apply migrations
```bash
docker compose -f local.yml run --rm django python manage.py migrate
```

#### Access Django shell
```bash
docker compose -f local.yml run --rm django python manage.py shell
```

#### Access PostgreSQL
```bash
docker compose -f local.yml exec postgres psql -U debug -d spade
```

### Dependency Management

#### Check installed package versions
```bash
docker compose -f local.yml run --rm django pip list
docker compose -f local.yml run --rm django pip list | grep -E "(Django|django-|rest|pytest)"
```

#### Check for dependency conflicts
```bash
docker compose -f local.yml run --rm django pip check
```
Should return "No broken requirements found" if all dependencies are compatible.

#### Check for outdated packages
```bash
docker compose -f local.yml run --rm django pip list --outdated
```
Shows available updates. Review carefully before upgrading major versions.

#### Upgrade dependencies
1. Edit `requirements/base.txt`, `requirements/local.txt`, or `requirements/production.txt`
2. Update version numbers (e.g., `django==5.2.3`)
3. Rebuild container:
```bash
docker compose -f local.yml build django
```
4. Restart services:
```bash
docker compose -f local.yml up -d
```
5. Run tests to verify:
```bash
docker compose -f local.yml run --rm django pytest
```

#### Fix common dependency issues:

**Django version conflict:**
```bash
# Keep Django 5.2.3 (not 6.0) for dj-rest-auth compatibility
# Edit requirements/base.txt: django==5.2.3
docker compose -f local.yml build django
```

**Dependency conflict resolution:**
```bash
# Check what's causing the conflict
docker compose -f local.yml run --rm django pip check

# View dependency tree
docker compose -f local.yml run --rm django pip show <package-name>
```

**Major version upgrades (handle with care):**
- Django 5 → 6: Breaking changes, test thoroughly
- Frictionless 4 → 5: Major API changes
- isort 6 → 7: Configuration changes
- pylint 3 → 4: New rules and breaking changes

### Maintenance Checklist
- [ ] All services start: `docker compose -f local.yml ps`
- [ ] Tests pass: 47/47 tests passing
- [ ] Pre-commit hooks pass: 16/16 hooks
- [ ] No dependency conflicts: `pip check` returns clean
- [ ] No database migration warnings
- [ ] API responding: `curl http://localhost:8081/api/v1/`
- [ ] Admin accessible: `http://localhost:8081/admin/`

### Common Issues

#### Port conflicts
```bash
# Check what's using port 8081
lsof -ti:8081 | xargs kill -9
```

#### Database issues
```bash
# Reset database
docker compose -f local.yml down -v
docker compose -f local.yml up -d postgres
docker compose -f local.yml run --rm django python manage.py migrate
```

#### Cache issues
```bash
# Clear Python cache
docker compose -f local.yml run --rm django find . -type d -name __pycache__ -exec rm -r {} +
```

### Tech Stack
- **Framework**: Django 5.2.3, Django REST Framework 3.16.1
- **Database**: PostgreSQL 16
- **Testing**: pytest 9.0.2, pytest-django 4.11.1, Factory Boy, Faker
- **Code Quality**: Ruff, Black 25.11.0, Pre-commit 4.4.0
- **Auth**: django-allauth 65.13.1, dj-rest-auth 7.0.1
- **Python**: 3.13.10

## Examples

`spadeapp.examples` contains some examples for basic objects such as executor, processor, and history provider.
