# [BEAD 2024 Practice Project - Group 1] Integration Scripts

This folder contains a Python web server to periodically pull taxi availability information from LTA DataMall.

## Pre-requisites

-   [python](https://www.python.org/downloads/)

## Quickstart

1. Create a new `.env` file to change based on the sample

```bash
cp .env.sample .env
```

2. Set the environment variables

```bash
# Account key to be used in LTA DataMall API calls
# (SECRET)
export LTA_ACCOUNT_KEY=

# Account key to be used in One Map API calls
# (SECRET)
export ONE_MAP_ACCOUNT_KEY=
```

3. Load the `.env` file and run the Python web server - the default root route returns all taxi availability

```bash
source .env
python -m flask --app script_server run --host=0.0.0.0 --port=8080
```
