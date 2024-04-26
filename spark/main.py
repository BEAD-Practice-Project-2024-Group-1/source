from flask import Flask
from district_taxi_availability import get_district_taxi_availability
from ingest_s3_data import ingest_bucket
from process_taxi_availability_time import process_taxi_availability_time

app = Flask(__name__)

@app.route("/district-taxi-availability")
def read_taxi_availability():
    """
    Read data from the taxi_availability table and display latest taxi availability for each district

    Returns:
        JSON: The result of the SQL query as a JSON object
    """

    return get_district_taxi_availability()


@app.route("/s3-ingest")
def pull_s3_data():
    """
    Pull data from S3, format and store in database
    """

    ingest_bucket()
    
    return "Sucess!"


@app.route("/process-taxi-availability-time")
def process_taxi_availability_time_handler():
    """
    Create time and day information for each batch
    """

    process_taxi_availability_time()
    
    return "Sucess!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
    