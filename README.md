# [BEAD 2024 Practice Project - Group 1] Source

This repository contains all the source code for group 1's project in a big mono repo.

## Pre-requisites

-   [Docker](https://www.docker.com/)

## Steps:

1. Make a copy of `.env.sample` and rename it to `.env`

    ```bash
    cp .env.sample .env
    ```

2. Fill up all the environment variables appropriately - each one has a description of what they are for inline
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
    LTA_ACCOUNT_KEY=I_REALLY_LOVE_NUS

    # Account key to be used in One Map API calls
    # (SECRET)
    # Value is example but MUST BE CHANGED to a valid One Map key - example will not work
    ONE_MAP_ACCOUNT_KEY=I_LOVE_NUS

    # URL to the script server
    # Example value but correct as a default - host must be docker network alias for the script server
    SCRIPT_URL=http://python-server:8080

    # Hostname for the database
    # Example value but correct as a default - must be docker network alias for the script server
    DATABASE_HOST=db

    # Address for Kafka Broker
    # Example value but correct as a default
    KAFKA_BROKER_ADDR=kafka-1:19092
    ```

3. Start up

   - Windows:

     a. Run the `init.bat` file to generate the `docker-compose` with absolute paths. On Windows, the `docker-compose` file's
     volume mappings do not work with relative paths so the `init.bat` will generate a modified compose file for you

     ```
     init.bat
     ```

     b. Run the docker compose file:

     ```
     docker compose -f docker-compose_windows.yml up -d
     ```

   - MacOS / Linux:

     Note: You only need to run `source .env` if your environment is already polluted from the development env vars

     ```bash
     source .env
     docker compose up
     ```

4. View the output

   The default web application is served at [http://locahost:4173](http://locahost:4173).

   We have a Python Flask server running at [http://localhost:8000](http://localhost:8000), it's used to conveniently trigger
 Spark jobs.

   To pull the data from S3 (public bucket, please don't spam) - [http://localhost:8000/s3-ingest](http://localhost:8000/s3-ingest)
and wait for it to download, it might take a minute or so.

   After ingesting the data, the timeline on the web visualization at [http://locahost:4173](http://locahost:4173) will
have data for you to view.

   You can also get information for the aggregation of taxi availability per district (counts of each point in each district) at [http://localhost:8000/district-taxi-availability](http://localhost:8000/district-taxi-availability)

   We also have a batch job to convert all the taxi availability times to 'day of week' and 'time of day' for machine learning at [http://localhost:8000/process-taxi-availability-time](http://localhost:8000/process-taxi-availability-time) but this will have no visible change on the front end (format meant to be used for machine learning).

## Other Notes

To remove the container, volume, and images for the database - this is important if you need to re-run the `init.sql`
script for the DB (in case of schema changes), this is because it is baked onto the image on build.

```bash
docker compose down db
docker volume rm $(docker volume list | grep source | awk -F ' ' '{print $2}')
docker image rm $(docker image list | grep source-db | awk -F ' ' '{print $1}')
```
