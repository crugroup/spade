---
sidebar_position: 1
---

# Quickstart

To get Spade up and running all you need is `docker-compose`
    
```bash
curl -O https://crugroup.github.io/spade/docker-compose.yml
docker-compose up
```

or depending on your Docker compose version it might be:

```bash
docker compose up
```

Spade will be available at [http://localhost:8080](http://localhost:8080). To begin, just register a user and start creating processes.
The first registered user will be a Django superuser.

To add your own code, simply place in in `./user_code` and it will be available to use in the Spade UI.