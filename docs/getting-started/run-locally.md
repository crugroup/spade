---
sidebar_position: 2
---

# Run locally

## Backend

If you want to run Spade locally for development or testing purposes, you can do so by following the instructions below.

1. Clone the Spade repo (https://github.com/crugroup/spade)
2. Install the required dependencies by running `pip install -r requirements/local.txt`
3. Start the required services by running `docker-compose -f local.yml up -d postgres`
4. Set the exnvironment variables required for Django:
```bash
export DJANGO_READ_DOT_ENV_FILE=True
export DJANGO_ENV_FILE=.envs/.local/.local
```
5. Run the migrations by running `python manage.py migrate`
6. Start the server by running `python manage.py runserver`

This will bring up the Spade backend server on your local machine. You can access the server by visiting `http://localhost:8000` in your browser.

## Frontend

To run the frontend locally, you can do so by following the instructions below.

1. Clone the Spade UI repo https://github.com/crugroup/spade)
2. Install the required dependencies by running `yarn install`
3. Start the server by running `yarn start`

This will bring up the Spade frontend server on your local machine. You can access the server by visiting `http://localhost:5173` in your browser.