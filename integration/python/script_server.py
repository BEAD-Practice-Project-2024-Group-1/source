
from flask import Flask
import requests
import os
import uuid
import datetime

API_URL = "http://datamall2.mytransport.sg/ltaodataservice/Taxi-Availability"
SKIP_CONST = 500
QUERY_LIMIT = 10
DELAY_IN_SECONDS = 60
HEADERS = {
    "AccountKey": os.environ.get('LTA_ACCOUNT_KEY')
}

print("LTA Account Key: " + os.environ.get('LTA_ACCOUNT_KEY'))

app = Flask(__name__)

@app.route("/taxi-availability")
def get_taxis():
    skip_cursor = 0
    counter = 0
    more = True
    all_results = []

    batch_id = uuid.uuid4()
    created_at = datetime.datetime.now().isoformat()

    def mapper(e):
        e['lat'] = e.pop('Latitude', None)
        e['lon'] = e.pop('Longitude', None)
        e['b_id'] = batch_id
        e['created_at'] = created_at
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

ONEMAP_API_URL = "https://www.onemap.gov.sg/api/public/popapi/getAllPlanningarea"
ONEMAP_HEADERS = {
    "Authorization": os.environ.get('ONE_MAP_ACCOUNT_KEY')
}

@app.route("/districts")
def get_districts():
    response = requests.get(ONEMAP_API_URL, headers=ONEMAP_HEADERS)
    result = response.json()
    try:
        return result.get("SearchResults")
    except Exception as e:
        print(e)