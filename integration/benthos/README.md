# [BEAD 2024 Practice Project - Group 1] Benthos

This folder contains benthos configuration files to run for integration pipleines.

It contains a Python script to periodically pull taxi availability information from LTA DataMall. Benthos runs this
script and inserts all the data into the PostGIS database.

## Pre-requisites

-   [benthos](https://www.benthos.dev/)
-   [python](https://www.python.org/downloads/release/python-314/)

TODO: Containerize everything and allow single docker compose to run entire project

## Quickstart

1. Create a new `.env` file to change based on the sample

```bash
cp .env.sample .env
```

2. Set the LTA account key

```bash
export LTA_ACCOUNT_KEY=<YOUR_LTA_ACCOUNT_KEY_HERE>
```

3. Load the `.env` file and run the Benthos configuration file; it will run the Python script and pipe the output into the database

```bash
source .env
benthos -c bead.yaml
```

## Notes

`ALTER USER ... with PASSWORD '...'`

Python Script Only:

```bash
source .env
python get-all-taxi-availability.py
```
