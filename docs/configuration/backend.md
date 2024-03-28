---
sidebar_position: 1
---

# Backend

Spade backend configutation is done via [Django Settings](https://docs.djangoproject.com/en/5.0/topics/settings/).
Most of the options can be configured via environment variables.

There are 3 config files provided:
* [local.py](https://github.com/crugroup/spade/blob/develop/config/settings/local.py) - for local development
* [test.py](https://github.com/crugroup/spade/blob/develop/config/settings/test.py) - used during test execution
* [production.py](https://github.com/crugroup/spade/blob/develop/config/settings/production.py) - for production deployment used by
  the Spade docker image

Of course, you can create your own settings file and use it by setting the `DJANGO_SETTINGS_MODULE` environment variable.