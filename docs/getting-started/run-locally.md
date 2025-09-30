---
sidebar_position: 2
---

# Run locally

## Backend

If you want to run Spade locally for development or testing purposes, you can do so by following the instructions below.

1. Clone the Spade repo (https://github.com/crugroup/spade)
2. Install the required dependencies by running `pip install -r requirements/local.txt`
3. Start the required services by running `docker-compose -f local.yml up -d postgres`
4. Set the environment variables required for Django:
```bash
export DJANGO_READ_DOT_ENV_FILE=True
export DJANGO_ENV_FILE=.envs/.local/.local
```
5. Run the migration by running `python manage.py migrate`
6. Start the server by running `python manage.py runserver`

This will bring up the Spade backend server on your local machine. You can access the server by visiting `http://localhost:8000` in your browser.

## Frontend

To run the frontend locally:

1. Clone the Spade UI repo (https://github.com/crugroup/spadeui)
2. This project requires [yarn](https://yarnpkg.com/).
    You can install it globally on your machine.

Here is the recommended method for installing yarn with corepack for MacOS:

**macOS (with Homebrew)**
```bash
brew install node
npm install --global yarn
corepack enable
corepack prepare yarn@4.6.0 --activate
```

**Windows (with Chocolatey)**
```powershell
choco install yarn
```
**Linux (Debian/Ubuntu)**
```bash
curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
sudo apt update && sudo apt install yarn
```
⚠️ For installing yarn on Windows and Linux have not been tested, please run those commands with caution.

3. Install the required dependencies by running `yarn install`
4. Start the server by running:
    - `yarn dev`: for local development
    - `yarn build && yarn start`: for production build + preview

This will bring up the Spade frontend server on your local machine. You can access the server by visiting `http://localhost:5173` in your browser for local development or `http://localhost:4173` in your browser for production build and preview.
