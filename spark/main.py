from flask import Flask
from district_taxi_availability import get_district_taxi_availability

app = Flask(__name__)

@app.route("/district-taxi-availability")
def read_taxi_availability():
    """
    Display latest taxi availability for each district

    Returns:
        JSON: The result of the SQL query as a JSON object
    """

    return get_district_taxi_availability()