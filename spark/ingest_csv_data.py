import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, udf


USER = os.environ['USER']
PASSWORD = os.environ['PASSWORD']
DATABASE_HOST = os.environ['DATABASE_HOST']

# (Assuming environment variables are set for connection details)
url = f"jdbc:postgresql://{DATABASE_HOST}:5432/bead"
properties = {
    "user": USER,
    "password": PASSWORD,
    "driver": "org.postgresql.Driver",
    "stringtype": "unspecified"
}

print("USER: " + USER)
print("PASSWORD: " + PASSWORD)
print("DATABASE_HOST: " + DATABASE_HOST)

def ingest_csv():
    fileNames = []
    for  files in os.walk("/app/csv"):
        for file in files:
            if file.endswith(".csv"):
                 fileNames.append(file)

    # Create SparkSession
    spark = SparkSession.builder.appName("Spark-PostgreSQL") \
        .config("spark.jars", './postgresql-42.7.3.jar') \
        .getOrCreate()

    @udf
    def create_point(lon, lat):
            return f"POINT({lon} {lat})"

    for fn in fileNames:
        df = spark.read.format("csv").option("header", False).load(fn)
        df = df.withColumn("location", create_point(col("_c2"), col("_c3")))
        df = df.withColumn("batch_id", col("_c0"))
        df = df.withColumn("created_at", col("_c1"))
        df = df.select("batch_id", "created_at", "location")
        df.write.jdbc(url=url, mode="append", table="taxi_availability", properties=properties)