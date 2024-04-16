# [BEAD 2024 Practice Project - Group 1] Source

This repository contains all the source code for group 1's project in a big mono repo.

## Pre-requisites

-   [Docker](https://www.docker.com/)

## Steps:

1. Make a copy of `.env.sample` and rename it to `.env`

```bash
cp .env.sample .env
```

2. Fill up all the environment variables appropraitely - each one has a description of what they are for inline
   as comments.

```bash
# Standardized username for all services (for convenience)
# Example value but correct as a default
USER=admin

# Standardized password for all services (for convenience)
# (SECRET)
# Example value but correct as a default
PASSWORD=password

# Account key to be used in LTA DataMall API calls
# (SECRET)
# Value is example but MUST BE CHANGED to a valid LTA DataMall key - example will not work
LTA_ACCOUNT_KEY=I_LOVE_ST

# URL to the script server
# Example value but correct as a default - host must be docker network alias for the script server
SCRIPT_URL=http://python-server:8080/

# Hostname for the database
# Example value but correct as a default - must be docker network alias for the script server
DATABASE_HOST=db
```

3. Just run the docker compose file and all services should start up fine

```bash
docker compose up
```

## Other Notes

To remove the container, volume, and images for the database

```bash
docker compose down db
docker volume rm $(docker volume list | grep source | awk -F ' ' '{print $2}')
docker image rm $(docker image list | grep source-db | awk -F ' ' '{print $1}')
```

You might also need to delete intermediate builds as the `init.sql` in ./datasources/bead_postgres is baked into the image.
