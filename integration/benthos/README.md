# [BEAD 2024 Practice Project - Group 1] Benthos

This folder contains benthos configuration files to run for integration pipleines.

It contains a Python script to periodically pull taxi availability information from LTA DataMall. Benthos runs this
script and inserts all the data into the PostGIS database.

## Pre-requisites

-   [benthos](https://www.benthos.dev/)
-   [python](https://www.python.org/downloads/release/python-314/)

TODO: Containerize everything and allow single docker compose to run entire project

## Quickstart

Benthos

```bash
source .env
LTA_ACCOUNT_KEY=$LTA_ACCOUNT_KEY benthos -c bead.yaml
```

## Notes

`ALTER USER ... with PASSWORD '...'`

Python Script Only:

```bash
source .env
LTA_ACCOUNT_KEY=$LTA_ACCOUNT_KEY python get-all-taxi-availability.py
```
