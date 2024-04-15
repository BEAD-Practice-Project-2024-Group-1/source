import sys
import requests
import os
import json
import time

API_URL = "http://datamall2.mytransport.sg/ltaodataservice/Taxi-Availability"
SKIP_CONST = 500
QUERY_LIMIT = 10
DELAY_IN_SECONDS = 60
HEADERS = {
    "AccountKey": os.environ.get('LTA_ACCOUNT_KEY')
}

while True:
    skip_cursor = 0

    counter = 0
    more = True

    while more and counter < QUERY_LIMIT:
        params = {
            "$skip": skip_cursor
        }

        counter += 1
        response = requests.get(API_URL, params=params, headers=HEADERS)
        results = response.json()

        number_of_results = len(results.get("value"))

        if number_of_results < SKIP_CONST:
            more = False

        for loc in results.get("value"):
            try:
                print(json.dumps(loc), flush=True)
            except (BrokenPipeError, IOError):
                pass

        skip_cursor += SKIP_CONST

    time.sleep(DELAY_IN_SECONDS)