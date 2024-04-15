# [BEAD 2024 Practice Project - Group 1] Datasources

This folder contains datasources to be used in the Spark processes.

## Pre-requisites

-   [...](...)

## Quickstart

```bash
...
```

## Notes

Remove the container, volume, and images for the database

```bash
docker compose down db
docker volume rm $(docker volume list | grep source | awk -F ' ' '{print $2}')
docker image rm $(docker image list | grep source-db | awk -F ' ' '{print $1}')
```

You might also need to delete intermediate builds.

```
insert into taxi_availability(location) values (ST_GeomFromText('POINT(-71.060316 48.432044)', 4326));
```
