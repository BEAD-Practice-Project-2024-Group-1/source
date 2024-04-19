
from flask import Flask
import requests
import os
import uuid

API_URL = "http://datamall2.mytransport.sg/ltaodataservice/Taxi-Availability"
SKIP_CONST = 500
QUERY_LIMIT = 10
DELAY_IN_SECONDS = 60
HEADERS = {
    "AccountKey": os.environ.get('LTA_ACCOUNT_KEY')
}

app = Flask(__name__)

@app.route("/taxi-availability")
def get_taxis():
    skip_cursor = 0
    counter = 0
    more = True
    all_results = []

    batch_id = uuid.uuid4()

    def mapper(e):
        e['lat'] = e.pop('Latitude', None)
        e['lon'] = e.pop('Longitude', None)
        e["b_id"] = batch_id
        return e

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

        all_results = all_results + list(map(mapper, results.get("value")))

        skip_cursor += SKIP_CONST

    try:
        return all_results
    except Exception as e:
        print(e)
        pass