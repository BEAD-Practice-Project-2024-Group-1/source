# [BEAD 2024 Practice Project - Group 1] Benthos

This folder contains benthos configuration files to run for integration pipleines.

It calls a Python script periodically to retrieve taxi availability, and pipes that output into a PostGIS database.

These are meant to be easily executed through the top-level docker-compose but Benthos can also be run directly here for testing purposes.

## Pre-requisites

-   [benthos](https://www.benthos.dev/)

## Quickstart

1. Create a new `.env` file to change based on the sample

```bash
cp .env.sample .env
```

2. Set the environment variables

```bash
# Standardized username for all services (for convenience)
export USER=...

# Standardized password for all services (for convenience)
# (SECRET)
export PASSWORD=...

# URL to the script server
export SCRIPT_URL=http://localhost:8080/

# Hostname for the database
export DATABASE_HOST=localhost

```

3. Load the `.env` file and run the Benthos configuration file; it will run the Python script and pipe the
   output into the database. Note that the Python script server and Database need to be running for this to work, just
   run the top level docker compose for that.

```bash
source .env
benthos -c ./config.yaml -r ./resources.yaml streams ./processOneMap.yaml ./processTaxiAvailability.yaml
```
